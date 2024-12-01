from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginview, name='login'),
    path('performlogin', views.performlogin,name='performlogin'),
    path('performlogout', views.performlogout, name='performlogout'),
    #CRUD Kelas Layanan
    path('create_kelas_layanan', views.create_kelas_layanan,name='create_kelas_layanan'),
    path('read_kelas_layanan', views.read_kelas_layanan, name='read_kelas_layanan'),
    path('update_kelas_layanan/<str:id>', views.update_kelas_layanan, name='update_kelas_layanan'),
    path('delete_kelas_layanan/<str:id>', views.delete_kelas_layanan, name='delete_kelas_layanan'),
    #CRUD Pemesanan
    path('create_pemesanan', views.create_pemesanan, name='create_pemesanan'),
    path('read_pemesanan', views.read_pemesanan, name='read_pemesanan'),
    path('update_pemesanan/<str:id>', views.update_pemesanan, name='update_pemesanan'),
    path('delete_pemesanan/<str:id>', views.delete_pemesanan, name='delete_pemesanan'),
    path('notapdf<str:idpemesanan>', views.notapdf, name='notapdf'),
    #CRUD Detail Pemesanan
    path('create_detailpemesanan/<int:idpemesanan>', views.create_detailpemesanan, name='create_detailpemesanan'),
    path('read_detailpemesanan', views.read_detailpemesanan, name='read_detailpemesanan'),
    path('update_detailpemesanan/<str:id>', views.update_detailpemesanan, name='update_detailpemesanan'),
    path('delete_detailpemesanan/<str:id>', views.delete_detailpemesanan, name='delete_detailpemesanan'),
    #CRUD Detail Kelas Layanan
    path('create_detailkelaslayanan/<str:idbis>', views.create_detailkelaslayanan, name='create_detailkelaslayanan'),
    path('read_detailkelaslayanan', views.read_detailkelaslayanan, name='read_detailkelaslayanan'),
    path('update_detailkelaslayanan/<str:id>', views.update_detailkelaslayanan, name='update_detailkelaslayanan'),
    path('delete_detailkelaslayanan/<str:id>', views.delete_detailkelaslayanan, name='delete_detailkelaslayanan'),
    #CRUD Bis
    path('create_bis', views.create_bis, name='create_bis'),
    path('read_bis', views.read_bis, name='read_bis'),
    path('update_bis/<str:id>', views.update_bis, name='update_bis'),
    path('delete_bis/<str:id>', views.delete_bis, name='delete_bis'),
    #CRUD  Penumpang
    path('create_penumpang', views.create_penumpang, name='create_penumpang'),
    path('read_penumpang', views.read_penumpang, name='read_penumpang'),
    path('update_penumpang/<str:id>', views.update_penumpang, name='update_penumpang'),
    path('delete_penumpang/<str:id>', views.delete_penumpang, name='delete_penumpang'),
    #CRUD Layanan Tambahan
    path('create_layanan_tambahan/<str:idbis>', views.create_layanan_tambahan, name='create_layanan_tambahan'),
    path('create_layanan_tambahan', views.create_layanan_tambahan, name='create_layanan_tambahan'),
    path('read_layanan_tambahan', views.read_layanan_tambahan, name='read_layanan_tambahan'),
    path('update_layanan_tambahan/<str:id>', views.update_layanan_tambahan, name='update_layanan_tambahan'),
    path('delete_layanan_tambahan/<str:id>', views.delete_layanan_tambahan, name='delete_layanan_tambahan'),
    #Laporan
    path('create_laporan', views.create_laporan, name='create_laporan'),
    path('laporanpdf', views.laporanpdf, name='laporanpdf'),
    #Dashboard
    path('dashboard', views.dashboard, name='dashboard'),
]

