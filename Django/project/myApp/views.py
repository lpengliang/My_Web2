from django.shortcuts import render,redirect
from .models import Wheel,Nav,Mustbuy,Shop,MainShow,Foodtypes,Goods,User,Cart,Order
from django.http import JsonResponse
import time
import random
from  django.conf import settings
import os
# Create your views here.


def home(request):
    wheelslist = Wheel.objects.all()
    navList = Nav.objects.all()
    mustbuyList =Mustbuy.objects.all()

    shopList = Shop.objects.all()
    shop1 = shopList[0]
    shop2 = shopList[1:3]
    shop3 = shopList[3:7]
    shop4 = shopList[7:11]

    mainList= MainShow.objects.all()

    return render(request, 'myApp/home.html', {"title": "主页", "wheelslist":wheelslist,"navList": navList ,
"mustbuyList":mustbuyList,"shop1":shop1,"shop2":shop2,"shop3":shop3,"shop4":shop4, "mainList":mainList})


def market(request, categoryid, cid, sortid):
    leftSlider=Foodtypes.objects.all()

    if cid == '0':
        productList = Goods.objects.filter(categoryid=categoryid)
    else:
        productList = Goods.objects.filter(categoryid=categoryid, childcid=cid)

        # 排序
    if sortid == '1':
        productList = productList.order_by("productnum")
    elif sortid == '2':
        productList = productList.order_by("price")
    elif sortid == '3':
        productList = productList.order_by("-price")

    group = leftSlider.get(typeid=categoryid)
    childList = []
    # 全部分类:0#进口水果:103534#国产水果:103533
    childnames = group.childtypenames
    arr1 = childnames.split("#")
    for str in arr1:
        # 全部分类:0
        arr2 = str.split(":")
        obj = {"childName": arr2[0], "childId": arr2[1]}
        childList.append(obj)


    #显示之前购物车产品的数量
    cartslist=[]
    token = request.session.get("token")
    if token:
        user=User.objects.get(userToken=token)
        cartslist=Cart.objects.filter(userAccount=user.userAccount)
        for p in productList:
            for c in cartslist:
                if c.productid == p.productid:
                    p.num = c.productnum

    return render(request, 'myApp/market.html', {"title":"闪送超市","leftSlider":leftSlider,
"productList":productList,"childList":childList,"categoryid":categoryid,"cid":cid})


def cart(request):
    cartslist = []
    token = request.session.get("token")
    if token != None:
        user = User.objects.get(userToken=token)
        cartslist = Cart.objects.filter(userAccount=user.userAccount)

    return render(request, 'myApp/cart.html', {"title": "购物车", "cartslist": cartslist})
#修改购物车
def changecart(request,flag):
    token = request.session.get("token")
    if token==None:
        #没登录
        return JsonResponse({"data":-1,"status":"error"})

    productid = request.POST.get("productid")
    product = Goods.objects.get(productid=productid)
    user = User.objects.get(userToken=token)

    if flag =='0':
        if product.storenums == 0:
            return JsonResponse({"data":-2,"status":"error"})
        carts = Cart.objects.filter(userAccount=user.userAccount)
        c = None
        if carts.count()==0:
        # 直接增加一条订单
            c = Cart.createcart(user.userAccount,productid,1,product.price,True,product.productimg,product.productname,False)
            c.save()
        else:
            try:
                c = carts.get(productid=productid)
                c.productnum += 1
                c.productprice = "%.2f"%(float(product.price) * c.productnum)
                c.save()
            except Cart.DoesNotExist as e:
                #直接增加一条订单
                c = Cart.createcart(user.userAccount, productid, 1, product.price, True, product.productimg,
                                    product.productname, False)
                c.save()
        #库存减一
        product.storenums -= 1
        product.save()
        return JsonResponse({"data":c.productnum,"price":c.productprice,"status":"success"})

    elif flag == '1':
        carts =Cart.objects.filter(userAccount= user.userAccount)
        c = None
        if carts.count()==0:

            return JsonResponse({"data": -2, "status": "error"})
        else:
            try:
                c = carts.get(productid=productid)
                c.productnum -= 1
                c.productprice = "%.2f"%(float(product.price) * c.productnum)
                if c.productnum==0:
                    c.delete()
                else:
                    c.save()
            except Cart.DoesNotExist as e:

                return JsonResponse({"data": -2, "status": "error"})
        #库存加一
        product.storenums += 1
        product.save()
        return JsonResponse({"data":c.productnum,"price":c.productprice,"status":"success"})
    elif flag=='2':
        carts = Cart.objects.filter(userAccount=user.userAccount)
        c = carts.get(productid=productid)
        c.isChose = not c.isChose
        c.save()
        str = ""
        if c.isChose:
            str = "√"
        return JsonResponse({"data":str,"status":"success"})

def saveorder(request):
    # 判断用户是否登录
    token = request.session.get("token")
    if token == None:
        return JsonResponse({"data": -1, "status": "error"})

    user = User.objects.get(userToken=token)
    carts = Cart.objects.filter(isChose=True)
    if carts.count() == 0:
        return JsonResponse({"data": -1, "status": "error"})

    oid = time.time() + random.randrange(1, 10000)
    oid = "%d" % oid
    o = Order.createorder(oid, user.userAccount, 0)
    o.save()
    for item in carts:
        item.isDelete = True
        item.orderid = oid
        item.save()
    return JsonResponse({"status": "success"})













def mine(request):
    username = request.session.get("username","未登录")
    token    = request.session.get("token",None)
    if token:
        user = User.objects.get(userToken=token)
        userimg = "/static/mdeia/"+ user.userAccount+".png"
        print("********")
        print(userimg)
    else:
        #默认头像
        userimg="/static/mdeia/1.png"
    return render(request, 'myApp/mine.html', {'title': "我的","username":username,"userimg":userimg})

# 登陆
from .forms.login import LoginForm
# from django.http import HttpResponse
def login(request):
    if request.method == "POST":
        f = LoginForm(request.POST)
        if f.is_valid():
            # 信息格式没多大问题，验证账号和密码的正确性
            print("***************")
            name = f.cleaned_data["username"]
            pswd = f.cleaned_data["passwd"]
            try:
                user=User.objects.get(userAccount=name)
                if user.userPasswd != pswd:
                    return redirect('/login/')
            except User.DoesNotExist as e:
                return redirect('/login/')

            #登陆成功
            token = time.time()+ random.randrange(1, 100000)
            user.userToken = str(token)
            user.save()
            request.session["username"] = user.userName
            request.session["token"] = user.userToken

            return redirect('/mine/')
        else:
            return render(request, 'myApp/login.html', {"title": "登陆", "form": f,"error":f.errors})
    else:
        f = LoginForm()
        return render(request, 'myApp/login.html', {"title": "登陆","form":f})


#注册
def register(request):
    if request.method == "POST":
        userAccount = request.POST.get("userAccount")
        userPasswd = request.POST.get("userPass")
        userName = request.POST.get("userName")
        userPhone = request.POST.get("userPhone")
        userAdderss = request.POST.get("userAdderss")
        userRank = 0
        token=time.time()+random.randrange(1,100000)
        userToken = str(token)
        f = request.FILES["userImg"]
        userImg = os.path.join(settings.MDEIA_ROOT, userAccount+".png")
        with open(userImg , "wb") as fb:
            for data in f.chunks():
                fb.write(data)
        user = User.createuser(userAccount,userPasswd,userName,userPhone, userAdderss,userImg,userRank,userToken)
        user.save()
        request.session["username"] = userName
        request.session["token"] = userToken
        return redirect('/mine/')

    else:
        return render(request, 'myApp/register.html', {"title":"注册"})

#退出登录
from django.contrib.auth import logout
def quit(request):
    logout(request)
    return redirect('/mine/')

def checkuserid(request):
    userid = request.POST.get("userid")
    try:
        user = User.objects.get(userAccount = userid)
        return JsonResponse({"data":"改用户已经被注册","status":"error"})
    except User.DoesNotExist as e:
        return JsonResponse({"data":"可以注册","status":"success"})
