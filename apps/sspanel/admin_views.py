import tomd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from apps.custom_views import PageListView
from apps.mixin import StaffRequiredMixin
from apps.sspanel.forms import (
    AnnoForm,
    GoodsForm,
    SSNodeForm,
    VmessNodeForm,
    UserSSConfigForm,
)
from apps.sspanel.models import (
    Announcement,
    Donate,
    Goods,
    InviteCode,
    MoneyCode,
    PurchaseHistory,
    SSNode,
    VmessNode,
    NodeOnlineLog,
    Ticket,
    User,
    UserOnLineIpLog,
    UserCheckInLog,
    UserTraffic,
    UserSSConfig,
)


class NodeListView(StaffRequiredMixin, View):
    def get(self, request):
        context = {
            "node_list": list(SSNode.objects.all()) + list(VmessNode.objects.all())
        }
        return render(request, "backend/node_list.html", context=context)


class NodeView(StaffRequiredMixin, View):
    def get(self, request, node_type):
        if node_type == "vmess":
            form = VmessNodeForm()
        elif node_type == "ss":
            form = SSNodeForm()
        return render(request, "backend/node_detail.html", context={"form": form})

    def post(self, request, node_type):
        if node_type == "vmess":
            form = VmessNodeForm(request.POST)
        elif node_type == "ss":
            form = SSNodeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功！", extra_tags="添加成功")
            return HttpResponseRedirect(reverse("sspanel:backend_node_list"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form}
            return render(request, "backend/node_detail.html", context=context)


class NodeDetailView(StaffRequiredMixin, View):
    def get(self, request, node_type, node_id):
        if node_type == "vmess":
            vmess_node = VmessNode.objects.get(node_id=node_id)
            form = VmessNodeForm(instance=vmess_node)
        elif node_type == "ss":
            ss_node = SSNode.objects.get(node_id=node_id)
            form = SSNodeForm(instance=ss_node)

        return render(request, "backend/node_detail.html", context={"form": form})

    def post(self, request, node_type, node_id):
        if node_type == "vmess":
            node = VmessNode.objects.get(node_id=node_id)
            form = VmessNodeForm(request.POST, instance=node)
        elif node_type == "ss":
            node = SSNode.objects.get(node_id=node_id)
            form = SSNodeForm(request.POST, instance=node)

        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:backend_node_list"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            return render(request, "backend/node_detail.html", context={"form": form})


class NodeDeleteView(StaffRequiredMixin, View):
    def get(self, request, node_type, node_id):
        if node_type == "vmess":
            vmess_node = VmessNode.objects.get(node_id=node_id)
            vmess_node.delete()
        elif node_type == "ss":
            ss_node = SSNode.objects.get(node_id=node_id)
            ss_node.delete()
        messages.success(request, "成功啦", extra_tags="删除节点")
        return HttpResponseRedirect(reverse("sspanel:backend_node_list"))


class UserOnlineIpLogView(StaffRequiredMixin, View):
    def get(self, request):
        data = []
        for node in SSNode.get_active_nodes():
            data.extend(UserOnLineIpLog.get_recent_log_by_node_id(node.node_id))
        context = PageListView(request, data).get_page_context()
        return render(request, "backend/user_online_ip_log.html", context=context)


class UserSSConfigListView(StaffRequiredMixin, View):
    def get(self, request):
        context = PageListView(
            request, User.objects.all().order_by("-date_joined")
        ).get_page_context()

        return render(request, "backend/user_ss_config_list.html", context)


class UserSSConfigDeleteView(StaffRequiredMixin, View):
    def get(self, request, user_id):
        user = User.get_by_pk(user_id)
        user.delete()
        messages.success(request, "成功啦", extra_tags="删除用户")
        return HttpResponseRedirect(reverse("sspanel:backend_user_ss_config_list"))


class UserSSConfigSearchView(StaffRequiredMixin, View):
    def get(self, request):
        q = request.GET.get("q")
        contacts = User.objects.filter(
            Q(username__icontains=q) | Q(email__icontains=q) | Q(pk__icontains=q)
        )
        context = {"contacts": contacts}
        return render(request, "backend/user_ss_config_list.html", context=context)


class UserSSConfigDetailView(StaffRequiredMixin, View):
    def get(self, request, user_id):
        user_ss_config = UserSSConfig.get_by_user_id(user_id)
        form = UserSSConfigForm(instance=user_ss_config)
        return render(
            request, "backend/user_ss_config_detail.html", context={"form": form}
        )

    def post(self, request, user_id):
        user_ss_config = UserSSConfig.get_by_user_id(user_id)
        form = UserSSConfigForm(request.POST, instance=user_ss_config)
        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:backend_user_ss_config_list"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form, "user_ss_config": user_ss_config}
            return render(
                request, "backend/user_ss_config_detail.html", context=context
            )


class UserStatusView(StaffRequiredMixin, View):
    def get(self, request):
        today_register_user = User.get_today_register_user().values()[:10]
        # find inviter
        for u in today_register_user:
            try:
                u["inviter"] = User.objects.get(pk=u["inviter_id"])
            except User.DoesNotExist:
                u["inviter"] = "None"

        context = {
            "total_user_num": User.get_total_user_num(),
            "alive_user_count": NodeOnlineLog.get_all_node_online_user_count(),
            "today_checked_user_count": UserCheckInLog.get_today_checkin_user_count(),
            "today_register_user_count": len(today_register_user),
            "traffic_users": UserTraffic.get_user_order_by_traffic(count=10),
            "rich_users_data": Donate.get_most_donated_user_by_count(10),
            "today_register_user": today_register_user,
        }
        return render(request, "backend/user_status.html", context=context)


@permission_required("sspanel")
def system_status(request):
    """跳转到后台界面"""
    context = {"total_user_num": User.get_total_user_num()}
    return render(request, "backend/index.html", context=context)


@permission_required("sspanel")
def backend_invite(request):
    """邀请码生成"""
    # TODO 这里加入一些统计功能
    code_list = InviteCode.objects.filter(code_type=0, used=False, user_id=1)
    return render(request, "backend/invitecode.html", {"code_list": code_list})


@permission_required("sspanel")
def gen_invite_code(request):

    Num = request.GET.get("num")
    code_type = request.GET.get("type")
    for i in range(int(Num)):
        code = InviteCode(code_type=code_type)
        code.save()
    messages.success(request, "添加邀请码{}个".format(Num), extra_tags="成功")
    return HttpResponseRedirect(reverse("sspanel:backend_invite"))


@permission_required("sspanel")
def backend_charge(request):
    """后台充值码界面"""
    # 获取所有充值码记录
    obj = MoneyCode.objects.all()
    page_num = 10
    context = PageListView(request, obj, page_num).get_page_context()
    # 获取充值的金额和数量
    Num = request.GET.get("num")
    money = request.GET.get("money")
    if Num and money:
        for i in range(int(Num)):
            code = MoneyCode(number=money)
            code.save()
        messages.success(request, "添加{}元充值码{}个".format(money, Num), extra_tags="成功")
        return HttpResponseRedirect(reverse("sspanel:backend_charge"))
    return render(request, "backend/charge.html", context=context)


@permission_required("sspanel")
def backend_shop(request):
    """商品管理界面"""

    goods = Goods.objects.all()
    context = {"goods": goods}
    return render(request, "backend/shop.html", context=context)


@permission_required("sspanel")
def good_delete(request, pk):
    """删除商品"""
    good = Goods.objects.filter(pk=pk)
    good.delete()
    messages.success(request, "成功啦", extra_tags="删除商品")
    return HttpResponseRedirect(reverse("sspanel:backend_shop"))


@permission_required("sspanel")
def good_edit(request, pk):
    """商品编辑"""

    good = Goods.objects.get(pk=pk)
    # 当为post请求时，修改数据
    if request.method == "POST":
        # 转换为GB
        data = request.POST.copy()
        data["transfer"] = eval(data["transfer"]) * settings.GB
        form = GoodsForm(data, instance=good)
        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:backend_shop"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form, "good": good}
            return render(request, "backend/goodedit.html", context=context)
    # 当请求不是post时，渲染form
    else:
        data = {"transfer": round(good.transfer / settings.GB)}
        form = GoodsForm(initial=data, instance=good)
        context = {"form": form, "good": good}
        return render(request, "backend/goodedit.html", context=context)


@permission_required("sspanel")
def good_create(request):
    """商品创建"""
    if request.method == "POST":
        # 转换为GB
        data = request.POST.copy()
        data["transfer"] = eval(data["transfer"]) * settings.GB
        form = GoodsForm(data)
        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功！", extra_tags="添加成功")
            return HttpResponseRedirect(reverse("sspanel:backend_shop"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form}
            return render(request, "backend/goodcreate.html", context=context)
    else:
        form = GoodsForm()
        return render(request, "backend/goodcreate.html", context={"form": form})


@permission_required("sspanel")
def purchase_history(request):
    """购买历史"""
    obj = PurchaseHistory.objects.all()
    page_num = 10
    context = PageListView(request, obj, page_num).get_page_context()
    return render(request, "backend/purchasehistory.html", context=context)


@permission_required("sspanel")
def backend_anno(request):
    """公告管理界面"""
    anno = Announcement.objects.all()
    context = {"anno": anno}
    return render(request, "backend/annolist.html", context=context)


@permission_required("sspanel")
def anno_delete(request, pk):
    """删除公告"""
    anno = Announcement.objects.filter(pk=pk)
    anno.delete()
    messages.success(request, "成功啦", extra_tags="删除公告")
    return HttpResponseRedirect(reverse("sspanel:backend_anno"))


@permission_required("sspanel")
def anno_create(request):
    """公告创建"""
    if request.method == "POST":
        form = AnnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功", extra_tags="添加成功")
            return HttpResponseRedirect(reverse("sspanel:backend_anno"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form}
            return render(request, "backend/annocreate.html", context=context)
    else:
        form = AnnoForm()
        return render(request, "backend/annocreate.html", context={"form": form})


@permission_required("sspanel")
def anno_edit(request, pk):
    """公告编辑"""
    anno = Announcement.objects.get(pk=pk)
    # 当为post请求时，修改数据
    if request.method == "POST":
        form = AnnoForm(request.POST, instance=anno)
        if form.is_valid():
            form.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:backend_anno"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"form": form, "anno": anno}
            return render(request, "backend/annoedit.html", context=context)
    # 当请求不是post时，渲染form
    else:
        anno.body = tomd.convert(anno.body)
        context = {"anno": anno}
        return render(request, "backend/annoedit.html", context=context)


@permission_required("sspanel")
def backend_ticket(request):
    """工单系统"""
    ticket = Ticket.objects.filter(status=1)
    context = {"ticket": ticket}
    return render(request, "backend/ticket.html", context=context)


@permission_required("sspanel")
def backend_ticketedit(request, pk):
    """后台工单编辑"""
    ticket = Ticket.objects.get(pk=pk)
    # 当为post请求时，修改数据
    if request.method == "POST":
        title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        status = request.POST.get("status", 1)
        ticket.title = title
        ticket.body = body
        ticket.status = status
        ticket.save()

        messages.success(request, "数据更新成功", extra_tags="修改成功")
        return HttpResponseRedirect(reverse("sspanel:backend_ticket"))
    # 当请求不是post时，渲染
    else:
        context = {"ticket": ticket}
        return render(request, "backend/ticketedit.html", context=context)
