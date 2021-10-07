import numpy as np
import pandas as pd
import requests
import json
import itertools


class SanKey(object):
    """
    use echarts to generate sankey plots
    """

    def __init__(self, pandasdf, title):
        """
        param pandasdf: must be DataFrame in pandas，containing three columns: source, target, and value
        """
        self.__df = pandasdf
        self.__sankey_title = title
        self.__base_html = """
<!--
    THIS EXAMPLE WAS DOWNLOADED FROM https://echarts.apache.org/examples/zh/editor.html?c=sankey-energy
-->
<!DOCTYPE html>
<html style="height: 100%">
<head>
    <meta charset="utf-8">
</head>
<body style="height: 100%; margin: 0">
<div id="container" style="height: 100%"></div>

<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<!-- Uncomment this line if you want to dataTool extension
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/dist/extension/dataTool.min.js"></script>
-->
<!-- Uncomment this line if you want to use gl extension
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts-gl@2/dist/echarts-gl.min.js"></script>
-->
<!-- Uncomment this line if you want to echarts-stat extension
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts-stat@latest/dist/ecStat.min.js"></script>
-->
<!-- Uncomment this line if you want to use map
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/map/js/china.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/map/js/world.js"></script>
-->
<!-- Uncomment these two lines if you want to use bmap extension
<script type="text/javascript" src="https://api.map.baidu.com/api?v=2.0&ak=<Your Key Here>"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/dist/extension/bmap.min.js"></script>
-->
<script type="text/javascript">
    var dom = document.getElementById("container");
    var myChart = echarts.init(dom);
    var app = {};
    myChart.showLoading();
    var data = {
        "nodes": node_in_html,
        "links": link_in_html,
        "title": 'title_in_html'
    }
    var option = {
        title: {
            text: data.title
        },
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'sankey',
                data: data.nodes,
                links: data.links,
                emphasis: {
                    focus: 'adjacency'
                },
                lineStyle: {
                    color: 'gradient',
                    curveness: 0.5
                }
            }
        ]
    };
    myChart.hideLoading();
    myChart.setOption(option);
    if (option && typeof option === 'object') {
        myChart.setOption(option);
    }
</script>
</body>
</html>

"""

        self.__node_list = None
        self.__links_in_html = None
        self.__render_html = self.__base_html

    def trans_node_link(self):
        node_list = list(set(self.__df['source'].tolist() + self.__df['target'].tolist()))
        self.__node_list = json.dumps([{"name": i} for i in node_list])
        self.__links_in_html = self.__df.to_json(orient='records')

    def render_html_function(self):
        self.__render_html = self.__render_html.replace("node_in_html", self.__node_list)
        self.__render_html = self.__render_html.replace("link_in_html", self.__links_in_html)
        self.__render_html = self.__render_html.replace("title_in_html", self.__sankey_title)

    def save_html(self, filename):
        """
        param filename: filename ended with .html
        """
        self.__filename = filename
        with open(file=self.__filename, encoding='utf-8', mode='w') as f:
            f.write(self.__render_html)

    def __call__(self, *args, **kwargs):
        self.trans_node_link()
        self.render_html_function()

if __name__=="__main__":
  school = pd.read_csv("school_matched_original.csv").set_index("index")
  school = school[school["read_full"]>1000]
  sch_cop = []
  for index,i in enumerate(school["country"]):
      try:
          sch_lst = i.split(";")
          if len(sch_lst)==1:
              sch_cop.append([sch_lst[0],sch_lst[0]])
          else:
              sch_cop_pro = list(itertools.combinations(sch_lst,2))
              for a in sch_cop_pro:
                  sch_cop.append(sorted(list(a)))
      except:
          continue
   
  
  df_sch = pd.DataFrame(sch_cop,columns=["school_1","school_2"])
  df_sch["count"] = 1
  df_sch = df_sch.groupby(["school_1","school_2"]).count().reset_index()
  df_sch.columns = ["source","target","value"]
  df_sch["target"] = df_sch["target"]+" "
  
  sankey_plot = SanKey(pandasdf=df_sch[df_sch["value"]>10], title="country_biorxiv") 
  sankey_plot()
  sankey_plot.save_html(filename="sankey_plot_country.html")
