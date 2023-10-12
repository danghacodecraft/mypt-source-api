from django.db import models


class Department(models.Model):
    class Meta:
        db_table = 'department_tb'
    child_depart = models.CharField(max_length=30, primary_key=True)
    branch = models.CharField(max_length=30)
    chi_nhanh = models.CharField(max_length=30)
    parent_depart = models.CharField(max_length=30)
    child_depart1 = models.CharField(max_length=30)
    dien_giai = models.CharField(max_length=3000)
    code_child_depart = models.CharField(max_length=1000)

    def __str__(self):
        return self.child_depart