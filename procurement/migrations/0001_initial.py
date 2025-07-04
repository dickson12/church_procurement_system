# Generated by Django 4.2.23 on 2025-06-16 06:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier', models.CharField(max_length=200)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('terms', models.TextField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('expected_delivery_date', models.DateTimeField(blank=True, null=True)),
                ('actual_delivery_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('requester', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('approved_by', models.CharField(blank=True, max_length=100, null=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SupplierPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier', models.CharField(max_length=200)),
                ('score', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comments', models.TextField()),
                ('date_evaluated', models.DateTimeField(auto_now_add=True)),
                ('evaluator', models.CharField(max_length=100)),
                ('delivery_timeliness', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('quality_rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('communication_rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('purchase_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='performance_evaluations', to='procurement.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier_name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_terms', models.TextField()),
                ('document', models.FileField(blank=True, null=True, upload_to='quotations/')),
                ('is_selected', models.BooleanField(default=False)),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('validity_period', models.IntegerField(default=30, help_text='Validity period in days')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotations', to='procurement.purchaserequest')),
            ],
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_orders', to='procurement.purchaserequest'),
        ),
        migrations.CreateModel(
            name='GoodsReceivedNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_by', models.CharField(max_length=100)),
                ('date_received', models.DateTimeField()),
                ('remarks', models.TextField(blank=True)),
                ('inspection_status', models.CharField(choices=[('PENDING', 'Pending Inspection'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('PARTIALLY_ACCEPTED', 'Partially Accepted')], default='PENDING', max_length=20)),
                ('inspection_date', models.DateTimeField(blank=True, null=True)),
                ('inspector', models.CharField(blank=True, max_length=100, null=True)),
                ('inspection_notes', models.TextField(blank=True)),
                ('rejection_reasons', models.TextField(blank=True)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods_received_notes', to='procurement.purchaseorder')),
            ],
        ),
    ]
