from django.db import models

# Create your models here.

class Menu(models.Model):
    '''
    菜单表
    '''
    title = models.CharField(verbose_name='一级菜单名称', max_length=32)
    icon = models.CharField(verbose_name='图标', max_length=32)       # 去掉null=True，blank=True 表示图标不允许为空

    def __str__(self):
        return self.title


class Permission(models.Model):
    '''
    权限表
    '''

    title = models.CharField(verbose_name='权限名称', max_length=64)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)
    name = models.CharField(verbose_name='URL别名', max_length=32,unique=True)
    menu = models.ForeignKey(verbose_name='所属菜单',
                             to='Menu',
                             null=True,
                             blank=True,
                             help_text='null表示不是菜单; 非null表示是二级菜单',
                             on_delete=models.CASCADE)

    pid = models.ForeignKey(verbose_name='关联的权限',
                            to='Permission',
                            null=True,
                            blank=True,
                            related_name='parents',  #反向自关联时可能出点问题，因此要加上related_name(不明白)
                            help_text='对于非菜单权限需要选择一个可以成为菜单的权限，用户做默认展开和选中菜单',
                            on_delete=models.CASCADE)