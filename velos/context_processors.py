def is_admin(request):
    return{'is_admin':request.user.groups.filter(name='admin').exists()}
def is_owner(request):
    return{'is_owner':request.user.groups.filter(name='owner').exists()}
def is_petugas(request):
    return{'is_petugas':request.user.groups.filter(name='petugas').exists()}