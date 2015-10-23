# option_calculator
    
期权组合监控计算器    
version0.0.2    
    
底层库类依赖:    
python3.x   
pyqt, matplotlib, pandas, numpy, scipy    
(建议直接安装anaconda3-x86-64)   
https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda3-2.3.0-Windows-x86_64.exe 
    
    
计划(已)实现功能:    
单个期权头寸统计量计算&监控(已填)    
自定义头寸组合的统计量计算&监控(已填)    
希腊值敏感性分析图(已填)    
期权组合到期损益分析图(已填)    
包含现货的组合头寸支持(已填)    
期权程序化交易算法单(大坑,深不见底,API不开,估计要弃)    
    
暂时通过wind客户端的python-api获取行情数据(慢...)    
启动程序前请先打开wind终端...     
    
使用说明:    
默认年化无风险利率为3%    
一年共250个交易日    
使用经典BS定价公式(所以只支持欧式期权)    
    
期权greek在options表中显示的是不带买卖方向和手数的原始值      
使用实时更新的最新价计算隐含波动率,反推greek    
    
lots列显示的是"手数",而非净数量    
    
portfolio的复选框勾选时,使用portfolio表中选中的所有行的group_id筛选头寸,    
未勾选,则从option和stock表中提取所有选中的行汇总作图    
    
安装:    
安装anaconda3    
用wind客户端修复python插件(WindPy)
启动wind并登录
解压缩option_monitor到任意目录
运行exec_run.pyw

恳请各位路过又恰巧有wind终端的大牛帮忙试用,多提意见    
mail: tpoy@live.cn




