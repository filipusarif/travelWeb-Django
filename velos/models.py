from django.db import models

# Create your models here.
class penumpang(models.Model):
    idpenumpang = models.AutoField(primary_key=True)  
    nama = models.CharField(max_length=100)          
    notelp = models.CharField(max_length=15)         
    email = models.EmailField()                     
    umur = models.IntegerField()
    def __str__(self):
        return str(self.nama)

class bis(models.Model):
    idbis = models.AutoField(primary_key=True)
    nomorbis = models.CharField(max_length=10)
    jadwal = models.DateTimeField()
    def __str__(self):
        return f"bis {self.nomorbis}"

class kelaslayanan(models.Model):
    idkelaslayanan = models.AutoField(primary_key=True)
    namakelaslayanan = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.namakelaslayanan}"

class detailkelaslayanan(models.Model):
    iddetailkelaslayanan = models.AutoField(primary_key=True)
    idbis = models.ForeignKey('bis', on_delete=models.CASCADE)
    idkelaslayanan = models.ForeignKey(kelaslayanan, on_delete=models.CASCADE)
    kapasitas = models.IntegerField(default=0)    
    def __str__(self):
        return f"{self.idbis}"

class layanantambahan(models.Model):
    idlayanantambahan = models.AutoField(primary_key=True)
    namalayanan = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)   
    def __str__(self):
        return f"{self.namalayanan} - Rp {self.harga}"
    
class pemesanan(models.Model):
    idpemesanan = models.AutoField(primary_key=True)
    idpenumpang = models.ForeignKey(penumpang, on_delete=models.CASCADE)
    iddetailkelaslayanan = models.ForeignKey(detailkelaslayanan, on_delete=models.CASCADE)
    def __str__(self):
        return f"pemesanan {self.idpemesanan} - penumpang: {self.idpenumpang.nama}"
    
class detailpemesanan(models.Model):
    iddetailpemesanan = models.AutoField(primary_key=True)
    idpemesanan = models.ForeignKey(pemesanan, on_delete=models.CASCADE)
    idlayanantambahan = models.ForeignKey(layanantambahan, on_delete=models.CASCADE)
    def __str__(self):
        return f"detail pemesanan {self.iddetailpemesanan} - layanan: {self.idlayanantambahan.namalayanan}"