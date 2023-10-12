from django.db import models

class Screen(models.Model):

	class Meta:
		db_table='mypt_profile_screen'

	id = models.IntegerField(primary_key=True)
	group = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	deleted_at = models.DateTimeField(null=True)