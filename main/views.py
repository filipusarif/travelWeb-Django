from django.shortcuts import render, redirect
from . import models 
from datetime import datetime 
import calendar
from django.http import HttpResponse 
from django. contrib import messages
from django. contrib. auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required 

from .decorators import role_required 
from django. forms import DateInput 
import json
from django.db.models import F,Q,Sum, Value 
import math


import tempfile 
from django.urls import reverse
from django.utils import timezone







# Create your views here.

def loginview(request):
    if request.user.is_authenticated:
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
    
        if group == 'owner' :
            return redirect('dashboard')
        elif group in ['admin', 'petugas']:
            return redirect('read_pemesanan')
        else:
            return redirect ('dashboard')
    else:
        return render (request,"base/login.html")
    
def performlogin(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed")  # Pastikan return response selalu ada
    else:
        username_login = request.POST.get('username')  # Menggunakan .get() untuk menghindari KeyError
        password_login = request.POST.get('password')

        if not username_login or not password_login:
            messages.error(request, "Username atau Password tidak boleh kosong!")
            return redirect("login")

        userobj = authenticate(request, username=username_login, password=password_login)

        if userobj is not None:
            login(request, userobj)
            messages.success(request, "Login Success")

            # Cek group user
            if userobj.groups.filter(name='admin').exists():
                return redirect("read_pemesanan")
            elif userobj.groups.filter(name='petugas').exists():
                return redirect("read_pemesanan")
            else:
                # Redirect jika user tidak memiliki group yang sesuai
                return redirect("dashboard")
        else:
            messages.error(request, "Username atau Password salah!")
            return redirect("login")

    # Tambahkan default response jika kondisi tidak terpenuhi
    return redirect("login")

    
@login_required(login_url="login")
def logoutview(request):
    logout(request)
    messages.info(request, "Berhasil Logout")
    return redirect ("login")

@login_required(login_url="login")
def performlogout(request):
    logout(request)
    return redirect("login")

#Kelas Layanan
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_kelas_layanan(request):
    kelas_layanan_obj = models.kelaslayanan.objects.all()
    if not kelas_layanan_obj.exists():
        messages.error(request, "Data Kelas Layanan Tidak Ditemukan!")

    return render(request, 'kelas_layanan/read_kelas_layanan.html', {
        'kelas_layanan_obj' : kelas_layanan_obj
    })

@login_required(login_url='login')
@role_required(['owner', 'admin'])
def create_kelas_layanan(request):
    if request.method == "GET":
        return render(request, 'kelas_layanan/create_kelas_layanan.html')

    else:
        namakelaslayanan = request.POST['namakelaslayanan']
        harga = request.POST['harga']
        models.kelaslayanan(
            namakelaslayanan=namakelaslayanan,
            harga=harga
        ).save()
        messages.success(request, 'Data Kelas Layanan berhasil ditambahkan!')

        return redirect('read_kelas_layanan')

@login_required(login_url='login')
@role_required(['owner', 'admin'])
def update_kelas_layanan(request, id):
    kelas_layanan_obj = models.kelaslayanan.objects.all()
    getkelaslayanan = models.kelaslayanan.objects.get(idkelaslayanan = id)
    if request.method == "GET":
        context = {
            'getkelaslayanan' : getkelaslayanan,
            'id' : id
        }
        return render(request, 'kelas_layanan/update_kelas_layanan.html', context)
    else:

        namakelaslayanan = request.POST['namakelaslayanan']
        harga = request.POST['harga']

        getkelaslayanan.idkelaslayanan = getkelaslayanan.idkelaslayanan
        getkelaslayanan.namakelaslayanan = namakelaslayanan
        getkelaslayanan.harga = harga

        getkelaslayanan.save()

        messages.success(request, 'Data Kelas Layanan berhasil diperbarui!')
        return redirect('read_kelas_layanan')

@login_required(login_url='login')
@role_required(['owner'])
def delete_kelas_layanan(request, id):
    getkelaslayanan = models.kelaslayanan.objects.get(idkelaslayanan=id)
    getkelaslayanan.delete()

    messages.error(request, 'Data Kelas Layanan berhasil dihapus!')
    return redirect('read_kelas_layanan')

#Pemesanan
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_pemesanan(request):
    pemesananobj = models.pemesanan.objects.all()
    pemesanan_data = []

    for pemesanan in pemesananobj:
        hargakelaslayanan = pemesanan.iddetailkelaslayanan.idkelaslayanan.harga

        layanantambahan = pemesanan.detailpemesanan_set.all()
        totalbiayalayanantambahan = sum(layanan.idlayanantambahan.harga for layanan in layanantambahan)

        total_harga = hargakelaslayanan + totalbiayalayanantambahan

        pemesanan_data.append({
            'pemesanan' : pemesanan,
            'total_harga' : total_harga,
        })

    return render(request, 'pemesanan/read_pemesanan.html', {
        'pemesanan_data' : pemesanan_data
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def create_pemesanan(request):
    penumpang_list = models.penumpang.objects.all()
    detailkelaslayanan_list = models.detailkelaslayanan.objects.all()

    if request.method == 'POST':
        idpenumpang = request.POST.get('idpenumpang')
        iddetailkelaslayanan = request.POST.get('iddetailkelaslayanan')

        # Ambil detail kelas layanan yang dipilih
        detail_kelas_layanan = models.detailkelaslayanan.objects.get(iddetailkelaslayanan=iddetailkelaslayanan)

        # Cek apakah kapasitas masih tersedia
        if detail_kelas_layanan.kapasitas <= 0:
            messages.error(request, 'Kapasitas kelas layanan ini sudah penuh. Tidak bisa melakukan pemesanan.')
            return redirect('create_pemesanan')

        # Jika kapasitas tersedia, buat pemesanan dan kurangi kapasitas sebesar 1
        models.pemesanan.objects.create(
            idpenumpang=models.penumpang.objects.get(idpenumpang=idpenumpang),
            iddetailkelaslayanan=detail_kelas_layanan
        )

        # Kurangi kapasitas sebanyak 1
        detail_kelas_layanan.kapasitas -= 1
        detail_kelas_layanan.save()

        messages.success(request, 'Pemesanan berhasil dilakukan!')
        return redirect('read_pemesanan')

    return render(request, 'pemesanan/create_pemesanan.html', {
        'penumpang_list': penumpang_list,
        'detailkelaslayanan_list': detailkelaslayanan_list
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def update_pemesanan(request, id) :
    penumpangobj = models.penumpang.objects.all()
    detailkelaslayananobj = models.detailkelaslayanan.objects.all()
    getpemesanan = models.pemesanan.objects.get(idpemesanan = id)
    nama = getpemesanan.idpenumpang.nama
    bis = getpemesanan.iddetailkelaslayanan.idbis
    kelaslayanan = getpemesanan.iddetailkelaslayanan.idkelaslayanan

    if request.method == 'GET' :
        return render(request, 'pemesanan/update_pemesanan.html', {
            'penumpangobj' : penumpangobj,
            'bis' : bis,
            'kelaslayanan' : kelaslayanan,
            'detailkelaslayananobj' : detailkelaslayananobj,
            'getpemesanan' : getpemesanan,
            'nama' : nama,
            'id' : id,
        })
    
    else :
        nama = request.POST['nama']
        # # idpenumpang = request.POST['idpenumpang']
        iddetailkelaslayanan = request.POST['iddetailkelaslayanan']

        # # pemesananobj = models.pemesanan.objects.filter(idpenumpang__nama = nama, iddetailkelaslayanan = iddetailkelaslayanan)
        # # if pemesananobj.exists() :
        # #     messages.error(request, 'Data Pemesanan Sudah Ada!')
        # #     return redirect('update_pemesanan', id)
        
        getpemesanan.idpemesanan = getpemesanan.idpemesanan
        getpemesanan.idpenumpang = models.penumpang.objects.get(nama = nama)
        getpemesanan.iddetailkelaslayanan = models.detailkelaslayanan.objects.get(iddetailkelaslayanan = iddetailkelaslayanan)
        
        getpemesanan.idpenumpang = getpemesanan.idpenumpang
        getpemesanan.iddetailkelaslayanan = getpemesanan.iddetailkelaslayanan
        getpemesanan.save()

        messages.success(request, 'Data Pemesanan Berhasil Diperbarui!')
        return redirect('read_pemesanan')
    
@login_required(login_url='login')
@role_required(['admin', 'owner'])
def delete_pemesanan(request, id):
    pemesanan_obj = models.pemesanan.objects.get(idpemesanan=id)

    # Tambah kembali kapasitas kelas layanan sebesar 1
    detail_kelas_layanan = pemesanan_obj.iddetailkelaslayanan
    detail_kelas_layanan.kapasitas += 1
    detail_kelas_layanan.save()

    # Hapus pemesanan
    pemesanan_obj.delete()
    messages.success(request, "Pemesanan berhasil dihapus, kapasitas kelas layanan telah dikembalikan.")
    return redirect('read_pemesanan')

#Detail Pemesanan
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_detailpemesanan(request):
    detailpemesananobj = models.detailpemesanan.objects.all()
    if not detailpemesananobj.exists():
        messages.error(request, "Data Detail Pemesanan Tidak Ditemukan!")

    return render(request, 'detailpemesanan/read_detailpemesanan.html', {
        'detailpemesananobj' : detailpemesananobj
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def create_detailpemesanan(request, idpemesanan) :
    pemesananobj = models.pemesanan.objects.get(idpemesanan = idpemesanan)
    layanantambahanobj = models.layanantambahan.objects.all()
    if request.method == 'POST' :
        idlayanantambahan = request.POST['idlayanantambahan']
        models.detailpemesanan.objects.create(
            idpemesanan = pemesananobj,
            idlayanantambahan = models.layanantambahan.objects.get(idlayanantambahan = idlayanantambahan),
        ).save()
        messages.success(request, 'Data Detail Pemesanan Berhasil Ditambahkan!')
        return redirect('read_pemesanan')
    
    return render(request, 'detailpemesanan/create_detailpemesanan.html', {
        'pemesananobj' : pemesananobj,
        'layanantambahanobj' : layanantambahanobj
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def update_detailpemesanan(request, id) :
    pemesananobj = models.pemesanan.objects.all()
    layanantambahanobj = models.layanantambahan.objects.all()
    getdetailpemesanan = models.detailpemesanan.objects.get(iddetailpemesanan = id)


    if request.method == 'GET' :
        return render(request, 'detailpemesanan/update_detailpemesanan.html', {
            'pemesananobj' : pemesananobj,
            'layanantambahanobj' : layanantambahanobj,
            'getdetailpemesanan' : getdetailpemesanan,

        })

    else :
        # idpemesanan = request.POST['idpemesanan']
        idlayanantambahan = request.POST['layanantambahan']

        # getdetailpemesanan.idpemesanan = models.pemesanan.objects.get(idpemesanan = idpemesanan)
        getdetailpemesanan.idlayanantambahan = models.layanantambahan.objects.get(idlayanantambahan = idlayanantambahan)

        getdetailpemesanan.save()

        messages.success(request, 'Data Detail Pemesanan Berhasil Diperbarui!')
        return redirect('read_pemesanan')
    
@login_required(login_url='login')
@role_required(['owner'])
def delete_detailpemesanan(request, id) :
    getdetailpemesanan = models.detailpemesanan.objects.get(iddetailpemesanan = id)
    getdetailpemesanan.delete()

    messages.error(request, "Data Detail Pemesanan berhasil dihapus!")
    return redirect('read_pemesanan')
    
#Detail Kelas Layanan
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_detailkelaslayanan(request):
    detailkelaslayananobj = models.detailkelaslayanan.objects.all()
    if not detailkelaslayananobj.exists():
        messages.error(request, "Data Detail Kelas Layanan Tidak Ditemukan!")

    return render(request, 'detailkelaslayanan/read_detailkelaslayanan.html', {
        'detailkelaslayananobj' : detailkelaslayananobj
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def create_detailkelaslayanan(request, idbis):
    bis_obj = models.bis.objects.get(idbis=idbis)
    kelaslayanan_list = models.kelaslayanan.objects.all()

    if request.method == 'POST':
        idkelaslayanan = request.POST.get('idkelaslayanan')
        kapasitas = request.POST.get('kapasitas')

        models.detailkelaslayanan.objects.create(
            idbis=bis_obj,
            idkelaslayanan=models.kelaslayanan.objects.get(idkelaslayanan=idkelaslayanan),
            kapasitas=kapasitas
        )
        messages.success(request, 'Detail Kelas Layanan berhasil ditambahkan!')
        return redirect('read_bis')

    return render(request, 'detailkelaslayanan/create_detailkelaslayanan.html', {
        'bis_obj': bis_obj,
        'kelaslayanan_list': kelaslayanan_list
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def update_detailkelaslayanan(request, id) :
    # bisobj = models.bis.objects.all()
    kelaslayanan_list = models.kelaslayanan.objects.all()
    detailkelaslayanan_obj = models.detailkelaslayanan.objects.get(iddetailkelaslayanan = id)
    # nomorbis = getdetailkelaslayanan.idbis.nomorbis
    # jadwal = getdetailkelaslayanan.idbis.jadwal
    # namakelaslayanan = getdetailkelaslayanan.idkelaslayanan.namakelaslayanan

    # if request.method == 'GET' :
    #     return render(request, 'detailkelaslayanan/update_detailkelaslayanan.html', {
    #         # 'bisobj' : bisobj,
    #         'kelaslayananobj' : kelaslayananobj,
    #         'getdetailkelaslayanan' : getdetailkelaslayanan,
    #         # 'nomorbis' : nomorbis,
    #         # 'jadwal' : jadwal,
    #         'namakelaslayanan' : namakelaslayanan,
    #         'id' : id
    #     })

    # else :
        # idbis = request.POST['idbis']
        # idkelaslayanan = request.POST['idkelaslayanan']
    if request.method == 'POST' :
        detailkelaslayanan_obj.idkelaslayanan = models.kelaslayanan.objects.get(idkelaslayanan=request.POST.get('idkelaslayanan'))
        detailkelaslayanan_obj.kapasitas = request.POST.get('kapasitas')
        detailkelaslayanan_obj.save()

        # getdetailkelaslayanan.iddetailkelaslayanan = getdetailkelaslayanan.iddetailkelaslayanan
        # # getdetailkelaslayanan.idbis = models.pemesanan.objects.get(idbis = idbis)
        # # getdetailkelaslayanan.idkelaslayanan = models.kelaslayanan.objects.get(idkelaslayanan = idkelaslayanan)
        # getdetailkelaslayanan.kapasitas = models.detailkelaslayanan.objects.get(kapasitas = kapasitas)
        # getdetailkelaslayanan.save()

        messages.success(request, 'Data Detail Kelas LayananBerhasil Diperbarui!')
        return redirect('read_bis')
    
    return render(request, 'detailkelaslayanan/update_detailkelaslayanan.html', {
        'detailkelaslayanan_obj' : detailkelaslayanan_obj,
        'kelaslayanan_list' : kelaslayanan_list
    })

@login_required(login_url='login')
@role_required(['owner'])
def delete_detailkelaslayanan(request, id) :
    getdetailkelaslayanan = models.detailkelaslayanan.objects.get(iddetailkelaslayanan = id)
    getdetailkelaslayanan.delete()

    messages.error(request, "Data Detail Kelaslayanan Berhasil Dihapus!")
    return redirect('read_bis')

#Bis
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_bis(request):
    bis_obj = models.bis.objects.all()
    if not bis_obj.exists():
        messages.error(request, "Data Bis Tidak Ditemukan!")
    return render(request, 'bis/read_bis.html', {
        'bis_obj' : bis_obj
    })

@login_required(login_url='login')
@role_required(['admin', 'owner'])
def create_bis(request) :
    if request.method == 'GET' :
        return render (request, 'bis/create_bis.html')
    
    else :
        nomorbis = request.POST['nomorbis']
        jadwal = request.POST['jadwal']

        models.bis(
            nomorbis = nomorbis,
            jadwal = jadwal
        ).save()
        messages.success(request, 'Data Bis Berhasil Ditambahkan!')

    return redirect('read_bis')

#Update Bis
@login_required(login_url='login')
@role_required(['admin', 'owner'])
def update_bis(request, id) :
    bis_obj = models.bis.objects.get(idbis=id)

    if request.method =="GET":
        context = {
            'bis_obj' : bis_obj,
            'id' : id,
        }
        return render(request, 'bis/update_bis.html', context)
    
    else :
        nomorbis = request.POST['nomorbis']
        jadwal = request.POST['jadwal']

        bis_obj.nomorbis = nomorbis
        bis_obj.jadwal = jadwal
        bis_obj.save()

        messages.success(request, 'Bis Berhasil Diperbarui')
        return redirect('read_bis')

# Delete Bis
@login_required(login_url='login')
@role_required(['owner'])
def delete_bis(request, id) :
    getbis = models.bis.objects.get(idbis = id)
    getbis.delete()

    messages.error(request, "Data Bis berhasil dihapus!")
    return redirect('read_bis')

# Create Penumpang
@login_required(login_url='login')
@role_required(['admin', 'owner'])
def create_penumpang(request):
    if request.method == 'GET':
        return render(request, 'penumpang/create_penumpang.html')
    else:
        idpenumpang = request.POST.get('idpenumpang')
        nama = request.POST.get('nama')
        notelp = request.POST.get('notelp')
        email = request.POST.get('email')
        umur = request.POST.get('umur')
        # Cek umur
        if int(umur) < 1:
            messages.error(request, 'Silahkan masukkan data umur yang benar!')
            return render(request, 'penumpang/create_penumpang.html', {
                'idpenumpang':idpenumpang,
                'nama': nama,
                'notelp': notelp,
                'email': email,
                'umur': umur,
            })
        # Cek jika ada field yang kosong
        if not nama or not email or not notelp or not umur:
            messages.error(request, 'Semua field harus diisi!')
            return render(request, 'penumpang/create_penumpang.html', {
                'idpenumpang':idpenumpang,
                'nama': nama,
                'notelp': notelp,
                'email': email,
                'umur': umur,
            })
        # Cek jika penumpang sudah ada
        penumpangobj = models.penumpang.objects.filter(idpenumpang=idpenumpang)
        if penumpangobj.exists():
            messages.error(request, 'Penumpang sudah ada!')
            return render(request, 'penumpang/create_penumpang.html', {
                'idpenumpang':idpenumpang,
                'nama': nama,
                'notelp': notelp,
                'email': email,
                'umur': umur,
            })
        # Jika tidak ada masalah, simpan data
        models.penumpang(
            idpenumpang=idpenumpang,
            nama=nama,
            notelp=notelp,
            email=email,
            umur=umur,
        ).save()
        messages.success(request, 'Data Penumpang berhasil ditambahkan!')
        return redirect('read_penumpang')
    
# Read penumpang
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_penumpang(request):
    penumpang_list = models.penumpang.objects.all()

    if not penumpang_list.exists():
        messages.error(request, "Tidak ada data penumpang yang ditemukan!")
    return render(request, 'penumpang/read_penumpang.html', {
        'penumpang_list': penumpang_list,

        'messages': messages.get_messages(request),
    })

# Update Penumpang
@login_required(login_url='login')
@role_required(['admin', 'owner'])
def update_penumpang(request, id):
    penumpang_obj = models.penumpang.objects.get(idpenumpang=id)
    if request.method == 'GET':
        context = {
            'penumpang_obj': penumpang_obj,
        }
        return render(request, 'penumpang/update_penumpang.html', context)
    else:
        nama = request.POST.get('nama')
        notelp = request.POST.get('notelp')
        email = request.POST.get('email')
        umur = request.POST.get('umur')
        if int(umur) < 0:
            messages.error(request, 'Umur tidak boleh negatif, silahkan masukkan data kembali!')
            return redirect('create_penumpang')
        if not nama or not email or not notelp or not umur:
            messages.error(request, 'Semua field harus diisi!')
            return redirect('update_penumpang', id=id)
        penumpang_obj.nama = nama
        penumpang_obj.notelp = notelp
        penumpang_obj.email = email
        penumpang_obj.umur = umur
        penumpang_obj.save()
        messages.success(request, 'Data Penumpang berhasil diperbarui!')
        return redirect('read_penumpang')

# Delete Penumpang
@login_required(login_url='login')
@role_required(['owner'])
def delete_penumpang(request, id):
    penumpang_obj = models.penumpang.objects.get(idpenumpang=id)
    penumpang_obj.delete()
    messages.success(request, 'Data Penumpang berhasil dihapus!')
    return redirect('read_penumpang')

#Read Layanan Tambahan
@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def read_layanan_tambahan(request):
    layanan_tambahan_obj = models.layanantambahan.objects.all()
    context = {
        'layanan_tambahan_obj': layanan_tambahan_obj,
    }
    return render(request, 'layanan_tambahan/read_layanan_tambahan.html', context)

#Create Layanan Tambahan
@login_required(login_url='login')
@role_required(['owner'])
def create_layanan_tambahan(request):
    if request.method == "GET":
        return render(request, 'layanan_tambahan/create_layanan_tambahan.html')

    else:
        namalayanan = request.POST['namalayanan']
        harga = request.POST['harga']

        layanan_tambahan_obj = models.layanantambahan.objects.filter(namalayanan=namalayanan)
        if layanan_tambahan_obj.exists():
            messages.error(request, 'Nama layanan tambahan sudah ada!')
        else:
            models.layanantambahan(
                namalayanan=namalayanan,
                harga=harga
            ).save()
            messages.success(request, 'Data layanan tambahan berhasil ditambahkan!')

        return redirect('read_layanan_tambahan')

#Update Layanan Tambahan
@login_required(login_url='login')
@role_required(['owner', 'admin'])
def update_layanan_tambahan(request, id):
    layanan_tambahan_obj = models.layanantambahan.objects.get(idlayanantambahan=id)

    if request.method == "GET":
        context = {
            'layanan_tambahan_obj': layanan_tambahan_obj,
            'id' : id,
        }
        return render(request, 'layanan_tambahan/update_layanan_tambahan.html', context)

    else:
        namalayanan = request.POST['namalayanan']
        harga = request.POST['harga']

        layanan_tambahan_obj.namalayanan = namalayanan
        layanan_tambahan_obj.harga = harga
        layanan_tambahan_obj.save()

        messages.success(request, 'Data layanan tambahan berhasil diperbarui!')
        return redirect('read_layanan_tambahan')

#Delete Layanan Tambahan
@login_required(login_url='login')
@role_required(['owner'])
def delete_layanan_tambahan(request, id):
    layanan_tambahan_obj = models.layanantambahan.objects.get(idlayanantambahan=id)
    layanan_tambahan_obj.delete()

    messages.error(request, "layanan tambahan berhasil di hapus!")
    return redirect('read_layanan_tambahan')

# Laporan
@login_required(login_url='login')
@role_required(['owner'])
def create_laporan(request):
    # Inisialisasi variabel untuk menyimpan data laporan
    bis_pemasukan = {}
    total_kelas_layanan = {}
    total_layanan_tambahan = {}
    grand_total_pemasukan = 0
    tanggal_mulai_date = None
    tanggal_akhir_date = None

    if request.method == "POST":
        # Ambil data tanggal mulai dan tanggal akhir dari form
        tanggal_mulai = request.POST.get('tanggal_mulai')
        tanggal_akhir = request.POST.get('tanggal_akhir')

        try:
            # Konversi string ke objek date
            tanggal_mulai_date = datetime.strptime(tanggal_mulai, '%Y-%m-%d')
            tanggal_akhir_date = datetime.strptime(tanggal_akhir, '%Y-%m-%d')

        except ValueError:
            messages.error(request, "Format tanggal salah. Gunakan format YYYY-MM-DD.")
            return render(request, 'laporan/create_laporan.html')

        # Filter pemesanan berdasarkan rentang tanggal
        pemesananobj = models.pemesanan.objects.filter(
            iddetailkelaslayanan__idbis__jadwal__range=(tanggal_mulai_date, tanggal_akhir_date)
        ).order_by('iddetailkelaslayanan__idbis__nomorbis')

        if not pemesananobj.exists():
            messages.error(request, "Data Pemesanan tidak ada untuk range tanggal yang dipilih.")
        else:
            for item in pemesananobj:
                nomorbis = item.iddetailkelaslayanan.idbis.nomorbis
                namakelaslayanan = item.iddetailkelaslayanan.idkelaslayanan.namakelaslayanan
                harga_kelas_layanan = item.iddetailkelaslayanan.idkelaslayanan.harga

                # Hitung total layanan tambahan untuk pemesanan ini
                detailpemesananobj = models.detailpemesanan.objects.filter(idpemesanan=item.idpemesanan)
                total_biaya_layanan_tambahan = sum(namalayanan.idlayanantambahan.harga for namalayanan in detailpemesananobj)

                layanan_tambahan_list = (namalayanan.idlayanantambahan.namalayanan for namalayanan in detailpemesananobj)
                total_pemasukan = harga_kelas_layanan + total_biaya_layanan_tambahan
                grand_total_pemasukan += total_pemasukan

                # Hitung total kelas layanan yang dipilih
                if namakelaslayanan in total_kelas_layanan:
                    total_kelas_layanan[namakelaslayanan] += 1
                else:
                    total_kelas_layanan[namakelaslayanan] = 1

                # Hitung total layanan tambahan yang dipilih
                for layanan in layanan_tambahan_list:
                    if layanan in total_layanan_tambahan:
                        total_layanan_tambahan[layanan] += 1
                    else:
                        total_layanan_tambahan[layanan] = 1

                # Tambahkan data ke bis_pemasukan dengan nomor bis sebagai key
                if nomorbis not in bis_pemasukan:
                    bis_pemasukan[nomorbis] = {
                        'kelas_layanan': namakelaslayanan,
                        'layanan_tambahan': layanan_tambahan_list,
                        'total_pemasukan': 0
                    }

                # Hitung pemasukan total untuk bis dan kelas layanan ini
                bis_pemasukan[nomorbis]['total_pemasukan'] += total_pemasukan

            context = {
                'bis_pemasukan': bis_pemasukan,
                'grand_total_pemasukan': grand_total_pemasukan,
                'total_kelas_layanan': total_kelas_layanan,
                'total_layanan_tambahan': total_layanan_tambahan,
                'tanggal_mulai': tanggal_mulai_date,
                'tanggal_akhir': tanggal_akhir_date,
            }

            print("bis pemasukan",bis_pemasukan)
            return render(request, 'laporan/create_laporan.html', context)

    # Jika metode bukan POST, tampilkan form kosong
    return render(request, 'laporan/create_laporan.html')

def laporanpdf(request):
    # Inisialisasi variabel untuk menyimpan data laporan
    bis_pemasukan = {}
    total_kelas_layanan = {}
    total_layanan_tambahan = {}
    grand_total_pemasukan = 0
    tanggal_mulai_date = None
    tanggal_akhir_date = None

    if request.method == "POST":
        # Ambil data tanggal mulai dan tanggal akhir dari form
        tanggal_mulai = request.POST.get('tanggal_mulai')
        tanggal_akhir = request.POST.get('tanggal_akhir')

        try:
            # Konversi string ke objek date
            tanggal_mulai_date = datetime.strptime(tanggal_mulai, '%Y-%m-%d').date()
            tanggal_akhir_date = datetime.strptime(tanggal_akhir, '%Y-%m-%d').date()

        except ValueError:
            messages.error(request, "Format tanggal salah. Gunakan format YYYY-MM-DD.")
            return render(request, 'laporan/create_laporan.html')

        # Filter pemesanan berdasarkan rentang tanggal
        pemesananobj = models.pemesanan.objects.filter(
                iddetailkelaslayanan__idbis__jadwal__range=(tanggal_mulai_date, tanggal_akhir_date)
            ).order_by('iddetailkelaslayanan__idbis__nomorbis')

        if not pemesananobj.exists():
            messages.error(request, "Data Pemesanan tidak ada untuk range tanggal yang dipilih.")
        else:
            for item in pemesananobj:
                nomorbis = item.iddetailkelaslayanan.idbis.nomorbis
                namakelaslayanan = item.iddetailkelaslayanan.idkelaslayanan.namakelaslayanan
                harga_kelas_layanan = item.iddetailkelaslayanan.idkelaslayanan.harga

                # Hitung total layanan tambahan untuk pemesanan ini
                detailpemesananobj = models.detailpemesanan.objects.filter(idpemesanan=item.idpemesanan)
                total_biaya_layanan_tambahan = sum(namalayanan.idlayanantambahan.harga for namalayanan in detailpemesananobj)

                layanan_tambahan_list = (namalayanan.idlayanantambahan.namalayanan for namalayanan in detailpemesananobj)
                total_pemasukan = harga_kelas_layanan + total_biaya_layanan_tambahan
                grand_total_pemasukan += total_pemasukan

                # Hitung total kelas layanan yang dipilih
                if namakelaslayanan in total_kelas_layanan:
                    total_kelas_layanan[namakelaslayanan] += 1
                else:
                    total_kelas_layanan[namakelaslayanan] = 1

                # Hitung total layanan tambahan yang dipilih
                for layanan in layanan_tambahan_list:
                    if layanan in total_layanan_tambahan:
                        total_layanan_tambahan[layanan] += 1
                    else:
                        total_layanan_tambahan[layanan] = 1

                # Tambahkan data ke bis_pemasukan dengan nomor bis sebagai key
                if nomorbis not in bis_pemasukan:
                    bis_pemasukan[nomorbis] = {
                        'kelas_layanan': namakelaslayanan,
                        'layanan_tambahan': layanan_tambahan_list,
                        'total_pemasukan': 0
                    }
                    
                # Hitung pemasukan total untuk bis dan kelas layanan ini
                bis_pemasukan[nomorbis]['total_pemasukan'] += total_pemasukan

    # Kirim data ke template HTML
    context = {
        'bis_pemasukan': bis_pemasukan,
        'grand_total_pemasukan': grand_total_pemasukan,
        'total_kelas_layanan': total_kelas_layanan,
        'total_layanan_tambahan': total_layanan_tambahan,
        'tanggal_mulai': tanggal_mulai_date,
        'tanggal_akhir': tanggal_akhir_date,
    }
    return render(request, 'laporan/laporanpdf.html', context)

# Dashboard 
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def dashboard(request):
    # Inisialisasi variabel
    pemasukan_bulanan = [0] * 12
    utilisasi_kelas = {}
    utilisasi_layanan = {}
    layanan_tambahan_list = []
    grand_total_pemasukan = 0

    pemesananobj = models.pemesanan.objects.all()
    
    for i in pemesananobj:
        harga_kelas_layanan = i.iddetailkelaslayanan.idkelaslayanan.harga
    # Hitung total layanan tambahan untuk pemesanan ini
        detailpemesananobj = models.detailpemesanan.objects.filter(idpemesanan=i.idpemesanan)
        total_biaya_layanan_tambahan = sum(namalayanan.idlayanantambahan.harga for namalayanan in detailpemesananobj)

        total_pemasukan = harga_kelas_layanan + total_biaya_layanan_tambahan
        grand_total_pemasukan += total_pemasukan

    # Pemasukan Bulanan (Line Chart)
    tahun = timezone.now().year
    pemesanan = models.pemesanan.objects.filter(iddetailkelaslayanan__idbis__jadwal__year=tahun)

    for i in pemesanan:
        bulan = i.iddetailkelaslayanan.idbis.jadwal.month - 1  # Bulan untuk index (0-based)
        harga_kelas = i.iddetailkelaslayanan.idkelaslayanan.harga
        layanan = models.detailpemesanan.objects.filter(idpemesanan=i.idpemesanan)
        total_harga_layanan_tambahan = sum(service.idlayanantambahan.harga for service in layanan)

        # Tambahkan pemasukan untuk bulan tersebut
        pemasukan_bulanan[bulan] += harga_kelas + total_harga_layanan_tambahan

    # Utilitas Kelas Layanan (Pie Chart)
    kelaslayanan = models.kelaslayanan.objects.all()
    for kelas in kelaslayanan:
        hitung_pemesanan = models.pemesanan.objects.filter(iddetailkelaslayanan__idkelaslayanan=kelas).count()
        if hitung_pemesanan > 0:
            utilisasi_kelas[kelas.namakelaslayanan] = hitung_pemesanan

    # Utilitas Layanan Tambahan (Pie Chart)
    layanan = models.layanantambahan.objects.all()
    for service in layanan:
        hitung_layanan_tambahan = models.detailpemesanan.objects.filter(idlayanantambahan=service).count()
        if hitung_layanan_tambahan > 0:
            utilisasi_layanan[service.namalayanan] = hitung_layanan_tambahan

    # Konversi ke format list untuk template
    list_bulan = [calendar.month_name[i] for i in range(1, 13)]
    nama_kelas = list(utilisasi_kelas.keys())
    total_kelas = list(utilisasi_kelas.values())
    nama_layanan = list(utilisasi_layanan.keys())
    total_layanan = list(utilisasi_layanan.values())

    return render(request, 'base/dashboard.html', {
        'pemasukan_bulanan': pemasukan_bulanan,
        'list_bulan': list_bulan,
        'nama_kelas': nama_kelas,
        'total_kelas': total_kelas,
        'nama_layanan': nama_layanan,
        'total_layanan': total_layanan,
        'grand_total_pemasukan': grand_total_pemasukan
    })

#Nota
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from . import models

@login_required(login_url='login')
@role_required(['admin', 'owner', 'petugas'])
def notapdf(request, idpemesanan):
    # Mengambil data pemesanan berdasarkan ID
    pemesananobj = get_object_or_404(models.pemesanan, idpemesanan=idpemesanan)

    # Mengambil layanan tambahan terkait
    layanantambahan = pemesananobj.detailpemesanan_set.all()
    totalbiayalayanantambahan = sum(layanan.idlayanantambahan.harga for layanan in layanantambahan)

    # Harga kelas layanan
    hargakelaslayanan = pemesananobj.iddetailkelaslayanan.idkelaslayanan.harga

    # Total harga
    total_harga = hargakelaslayanan + totalbiayalayanantambahan

    # Data yang akan dikirim ke template
    context = {
        'pemesananobj': pemesananobj,
        'layanantambahan': layanantambahan,
        'hargakelaslayanan': hargakelaslayanan,
        'totalbiayalayanantambahan': totalbiayalayanantambahan,
        'total_harga': total_harga,
    }

    # Render ke template HTML
    return render(request, 'pemesanan/notapdf.html', context)