# Generated migration for adding reorder_threshold to Product model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),  # Ajusta esto según tu última migración
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reorder_threshold',
            field=models.PositiveIntegerField(default=10, help_text='Umbral de reorden (cantidad mínima antes de alertar)'),
        ),
    ]
