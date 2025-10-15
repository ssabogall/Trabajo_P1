from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_comment_promotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
