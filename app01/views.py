from django.shortcuts import render, HttpResponse
from django import forms
from app01 import models
from django.forms import formset_factory


# Create your views here.

class MultiPermissionForm(forms.Form):
    title = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    url = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    name = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    menu_id = forms.ChoiceField(
            choices=[(None, '------')],
            widget=forms.Select(attrs={'class': "form-control"}),
            required=False,
    )
    pid_id = forms.ChoiceField(
            choices=[(None, '------')],
            widget=forms.Select(attrs={'class': "form-control"}),
            required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
                menu__isnull=True).values_list('id', 'title')

class MultiUpdatePermissionForm(forms.Form):

    id = forms.IntegerField(
        widget=forms.HiddenInput()      #这个ID不应该让用户看到，要隐藏在页面里
    )
    title = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    url = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    name = forms.CharField(
            widget=forms.TextInput(attrs={'class': "form-control"})
    )
    menu_id = forms.ChoiceField(
            choices=[(None, '------')],
            widget=forms.Select(attrs={'class': "form-control"}),
            required=False,
    )
    pid_id = forms.ChoiceField(
            choices=[(None, '------')],
            widget=forms.Select(attrs={'class': "form-control"}),
            required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
                menu__isnull=True).values_list('id', 'title')

def multi_add(request):
    '''
    批量添加
    :param request:
    :return:
    '''
    formset_class = formset_factory(MultiPermissionForm, extra=2)  # extra=5 表示生成5个 MultiPermissionForm 表单
    if request.method == 'GET':
        formset = formset_class()
        # print("formset:",formset)
        return render(request, 'multi_add.html', {'formset': formset})

    formset = formset_class(data=request.POST)
    # [form1(字段，错误信息), form2(字段，错误信息), form3(字段，错误信息),...]
    if formset.is_valid():  # 校验表单情况1：完全空的表单，formset.is_valid()校验通过， 校验表单情况2： 部分行为空的表单，formset.is_valid()校验通过
        # print(formset.cleaned_data)   #[{}, {}]  提交成功：[{'title': 'asdf', 'url': 'asdfa', 'name': 'asdfa', 'menu_id': '2', 'pid_id': ''}, {'title': 'asdf', 'url': 'asdfas', 'name': 'a', 'menu_id': '2', 'pid_id': ''}]
        flag = True
        post_row_list = formset.cleaned_data  # 检查 formset中没有错误信息，则将用户提交的数据获取到
        for i in range(0, formset.total_form_count()):
            row = post_row_list[i]
            if not row:  # 如果是空表单，跳过当前循环，返回提交成功
                continue
            # .cleaned_data数据格式 [{}， {}， {}]
            print(row)  # row 是字典
            # models.Permission.objects.create(**row)    #写入数据库的方式一
            try:
                obj = models.Permission(**row)  # 写入数据库的方式二
                obj.validate_unique()  # 检查当前对象在数据库是否存在唯一的异常
                obj.save()
            except Exception as e:
                # [{'title':[]}]
                formset.errors[i].update(e)  # 将错误信息放到form对象的错误字段
                flag = False
        if flag:
            return HttpResponse('提交成功')
        else:
            return render(request, 'multi_add.html', {'formset': formset})

    return render(request, 'multi_add.html', {'formset': formset})


def multi_edit(request):
    formset_class = formset_factory(MultiUpdatePermissionForm, extra=0)
    if request.method == 'GET':
        # formset = formset_class(
        #         initial=[
        #             {'id': 1, 'title':'x1', 'url': 'xxx'},
        #             {'id': 2, 'title':'x2', 'url': 'ooo'},
        #         ]
        # )
        formset = formset_class(initial=models.Permission.objects.all().values('id', 'title','name','url', 'menu_id','pid_id'))
        return render(request, 'multi_edit.html', {'formset': formset})

    formset = formset_class(data=request.POST)

    if formset.is_valid():
        post_row_list = formset.cleaned_data  # 检查 formset中没有错误信息，则将用户提交的数据获取到
        flag = True
        for i in range(0, formset.total_form_count()):
            row = post_row_list[i]
            if not row:  # 如果是空表单，跳过当前循环，返回提交成功
                continue
            permission_id = row.pop('id')
            # models.Permission.objects.filter(id=permission_id).update(**row)   #如果name字段重名，也会遇到唯一索引问题
            #避免索引问题，使用以下代码
            try:
                permission_object = models.Permission.objects.filter(id=permission_id).first()
                # permission_object.title = row['title']
                # permission_object.url = row['url']
                # permission_object.name = row['name']
                # permission_object.menu_id = row['menu_id']
                # permission_object.pid_id = row['pid_id']
                #利用反射优化以上5行代码
                for key, value in row.items():
                   setattr(permission_object, key, value)
                permission_object.validate_unique()
                permission_object.save()
            except Exception as e:
                formset.errors[i].update(e)
                flag = False
        if flag:
            return HttpResponse('提交成功')
        else:
            return render(request, 'multi_edit.html', {'formset': formset})
    return render(request, 'multi_edit.html', {'formset': formset})