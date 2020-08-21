from django.shortcuts import render, HttpResponse, redirect
from app1.models import Article
from app1.models import ArticleCategory
from app1.models import Attachment
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage,InvalidPage

# from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.forms.models import model_to_dict


# Create your views here.
def global_category(request):
# 所有分类第一层大类数据集
    category_list = ArticleCategory.objects.raw(
    "select id,slug,pid,title,order_number from article_category where pid=0 order by order_number;")
    return {'category_list':category_list}


# @csrf_exempt
def index(request):
    # 最新消息保持三天之内的内容
    latest_list = Article.objects.raw(
        "SELECT id,title from article where created > DATE_SUB(curdate(),INTERVAL 3 DAY) order by created desc;")
    # 所有分类第一层大类数据集
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0 order by order_number;")
    # 第二层分类
    subcategory_list = ArticleCategory.objects.raw(
        "select id,pid,slug,title,modified from article_category where pid in (select id from article_category where pid=0) order by pid,order_number;")

    # threecategory_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid not in (select id from article_category WHERE pid=0) and pid <> 0 ORDER BY pid,order_number")

    return render(request, "index.html", locals())


def article(request, p1, n1):
    # 所有分类第一层大类数据集
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0")
    # 包含页面所传过来的父类ID查询出来的本类分类第一层大类值
    category1_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where id=%s" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第二层列表，用与横向
    category2_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where pid=%s" % (p1))
    # # 包含页面所传过来的父类ID查询出来的本类分类第二层列表
    # subcategory_list = ArticleCategory.objects.raw(
    #     "select id,pid,slug,title,modified from article_category where pid=%s order by pid" % (p1))
    # # 包含页面所传过来的父类ID查询出来的本类分类第三层列表
    # threecategory_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid not in (select id from article_category WHERE pid=0) and pid <> 0 ORDER BY pid,order_number")
# 所传值n1所查询出相对应的文章
    new_list = Article.objects.raw("select id,title,content,created from article where id=%s" % (n1))
    print(new_list)

    return render(request, "article.html", locals())


def artlist(request,p, p1, p2):#传入值依次为：页码，大分类ID,小分类ID
    # 所有分类第一层大类数据集
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0")
    # 包含页面所传过来的父类ID查询出来的本类分类第一层值
    category1_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where id=%s" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第二层列表
    subcategory_list = ArticleCategory.objects.raw(
        "select id,pid,slug,title,modified from article_category where pid=%s order by pid" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第三层列表
    threecategory_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where pid not in (select id from article_category WHERE pid=0) and pid <> 0 ORDER BY pid,order_number")
    # 以传参过来所对应的第一层分类为条件查询得出来的本类文章结果集
    news_list = Article.objects.raw(
        "select id,title,content,created from article where id in (select article_id from article_category_mapping where category_id in "
        "(select id from article_category where pid in (select id from article_category where pid=%s) union all select id from article_category where pid=%s)) "
        "order by created desc" % (p1, p1))

    p=int(p)
    page_size = 5
    paginator = Paginator(news_list, page_size)  # 进行分页
    page_news = paginator.page(p)

    return render(request, "artlist.html", locals())

def artlista(request, p, p1, p2):
    # 所有分类第一层大类数据集
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0")
    # 包含页面所传过来的父类ID查询出来的本类分类第一层值
    category1_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where id=%s" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第二层列表
    subcategory_list = ArticleCategory.objects.raw(
        "select id,pid,slug,title,modified from article_category where pid=%s order by pid" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第三层列表
    threecategory_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where pid not in (select id from article_category WHERE pid=0) and pid <> 0 ORDER BY pid,order_number")
    # 以传参过来所对应的第一层分类为条件查询得出来的本类文章结果集
    news_list = Article.objects.raw(
        "select id,title,content,created from article where id in (select article_id from article_category_mapping where category_id in "
        "(select id from article_category where pid=%s) union all select article_id from article_category_mapping where category_id=%s) "
        "order by created desc" % (p2, p2))

    p = int(p)
    page_size = 5
    paginator = Paginator(news_list, page_size)  # 进行分页
    page_news = paginator.page(p)

    return render(request, "artlista.html", locals())

def searchlist(request,p):
    p = int(p)
    p1 = request.POST.get('kwtype')#从artlist.html获得P1,然后循环赋值给artlist.html
    if (p1 == None):
        p1 = request.GET.get('kwtype')
    keyword = request.POST.get('keyword')
    if (keyword== None):
        keyword = request.GET.get('keyword')
    kw = "%%" + str(keyword) + "%%"
    # 以POST提交的关键字为条件查询得出来的结果集
    news_list = Article.objects.raw(
        "select id,title,content,created from Article where id in (select article_id from article_category_mapping where category_id in "
        "(select id from article_category where pid=%s)) and (title like '%s' or content like '%s')" % (p1, kw, kw))
    page_size = 5
    paginator = Paginator(news_list, page_size)  # 进行分页
    page_news = paginator.page(p)

    # 主菜单数据
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0")
    # category_list = ArticleCategory.objects.raw(
    #     "select a.id,a.pid,a.title,b.id,b.pid,b.slug from (select id,pid,slug,title from article_category where pid=0) as a,"
    #     "(select id,pid,title,slug from article_category where pid in (select id from article_category  where pid=0) and order_number=1) as b where a.id=b.pid")
    # 包含页面所传过来的父类ID查询出来的本类分类第一层值
    category1_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where id=%s" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第二层列表
    subcategory_list = ArticleCategory.objects.raw(
        "select id,pid,slug,title,modified from article_category where pid=%s order by pid" % (p1))
    # 包含页面所传过来的父类ID查询出来的本类分类第三层列表
    threecategory_list = ArticleCategory.objects.raw(
        "select id,slug,pid,title,order_number from article_category where pid not in (select id from article_category WHERE pid=0) and pid <> 0 ORDER BY pid,order_number")

    return render(request, "artlists.html", locals())



def searchall(request,p):
    p = int(p)
    p1 = request.POST.get('ss_select') # 从artlist.html获得P1,然后循环赋值给artlist.html
    if (p1 == None):
        p1 = request.GET.get('ss_select')
    qt = request.POST.get('qt')
    if (qt== None):
        qt = request.GET.get('qt')
    kw = "%%" + str(qt) + "%%"

    if (p1 == '1'):
    # 主菜单数据
    #     category_list = ArticleCategory.objects.raw(
    #         "select id,slug,pid,title,order_number from article_category where pid=0")
        news_list = Article.objects.raw(
            "select id,title,content,created from Article where title like '%s' or content like '%s'" % (kw, kw))
        page_size = 5
        paginator = Paginator(news_list, page_size)  # 进行分页
        page_news=paginator.page(p)
        return render(request, "searchlist.html", locals())

    else:
    # 主菜单数据
    #     category_list = ArticleCategory.objects.raw(
    #         "select id,slug,pid,title,order_number from article_category where pid=0")
        news_list = Attachment.objects.raw(
            "select id,title,path as content,created from Attachment where title like '%s'" % (kw))
        page_size = 5
        paginator = Paginator(news_list, page_size)  # 进行分页
        page_news = paginator.page(p)
        return render(request, "searchlist1.html", locals())


def searchlista(request,p1):
    # 所有分类第一层大类数据集
    # category_list = ArticleCategory.objects.raw(
    #     "select id,slug,pid,title,order_number from article_category where pid=0")

    # 所传值p1所查询出相对应的文章
    new_list = Article.objects.raw("select id,title,content,created from article where id=%s" % (p1))
    print(new_list)

    return render(request, "searchlista.html", locals())
