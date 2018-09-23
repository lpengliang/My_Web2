from django.conf.urls import url
from . import views

urlpatterns = [

    #url(r'^', views.home, name="home"),
    url(r'^home/$', views.home, name="home"),
    url(r'^market/(\d+)/(\d+)/(\d+)/$', views.market, name="market"),


    url(r'^cart/$', views.cart, name="cart"),
    url(r'^mine/$', views.mine, name="mine"),

#登录 注册
    url(r'^login/$', views.login, name="login"),
    url(r'^register/$', views.register, name="register"),
#验证注册账号是否重复
    url(r'^checkuserid/$', views.checkuserid, name="checkuserid"),
#退出登录
    url(r'^quit/$', views.quit, name="quit"),
#修改购物车
    url(r'^changecart/(\d+)/$', views.changecart, name="changecart"),
#是否保存订单
    url(r'^saveorder/$', views.saveorder, name="saveorder"),



]