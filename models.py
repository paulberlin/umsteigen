from django.db import models
from datetime import date

# Create your models here.

class Line(models.Model):
    number = models.PositiveSmallIntegerField()
    line_type_choices = (
        ('s', 'S-Bahn'),
        ('u', 'U-Bahn'),
    )
    line_type = models.CharField(max_length=1, choices=line_type_choices)
    start = models.ForeignKey('Direction', blank=True, null=True, on_delete=models.CASCADE, related_name='start')
    end = models.ForeignKey('Direction', blank=True, null=True, on_delete=models.CASCADE, related_name='end')
    sequence_available = models.BooleanField(default=False)
    url = models.CharField(max_length=2000, null=True, blank=True)

    @property
    def line_id(self):
      return self.id

    @property
    def bvg_details(self):
      if self.line_type == 's':
        return 'https://sbahn.berlin/fahren/s' + str(self.number)
      return 'https://www.bvg.de/de/verbindungen/linienuebersicht/u' + str(self.number)
 
    @property
    def name(self):
        return str.upper(self.line_type) + str(self.number)
 
    @property
    def css(self):
        return str.lower(self.line_type) + "line " + str.lower(self.line_type) + str(self.number)

    @property
    def css_prefix(self):
        return str.lower(self.line_type) + str(self.number)

    def __str__(self):
        return self.name
 
    class Meta:
        ordering = ['line_type', 'number']

#class StationOnLine(models.Model):
#    sequence = models.SmallIntegerField(null=True, blank=True)
#    liine = models.ForeignKey('Line', blank=True, null=True, on_delete=models.CASCADE)
#    staation = models.ForeignKey('Station', blank=True, null=True, on_delete=models.CASCADE)
    
class Direction(models.Model):
    name = models.CharField(max_length = 200)
    line = models.ForeignKey('Line', blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.line.name + "->" + self.name

    class Meta:
        ordering = ['line', 'name']

class Station(models.Model):
    name = models.CharField(max_length = 200)
    url_name = models.CharField(max_length = 200, null=True, blank=True)
    #liness = models.ManyToManyField('Line', through='StationOnLine', related_name='liness')
    lines = models.ManyToManyField('Line')
    bvg_details = models.CharField(max_length=2000, null=True, blank=True)
    bvg_pic = models.CharField(max_length=2000, null=True, blank=True)
    bvg_pdf = models.CharField(max_length=2000, null=True, blank=True)
    bvg_levelguide = models.CharField(max_length=2000, null=True, blank=True)
    schema_pic = models.CharField(max_length=2000, null=True, blank=True)
    complete = models.BooleanField(default=False)
    change_station = models.BooleanField(default=False)
    sequence = models.BigIntegerField()
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)
    db_station_name = models.CharField(max_length = 200, null=True, blank=True)

    def __str__(self):
        return self.name + " (" + ", ".join([i.name for i in self.lines.all()]) + ")"

    @property
    def station_id(self):
      return self.id

    @property
    def last_modified(self):
      return Change.objects.filter(at__exact=self.id).order_by('-updated_at').values('updated_at')[0]['updated_at']

    @property
    def count(self):
        return Change.objects.filter(at__exact=self.id).count()

    @property
    def nice_name(self):
        return self.name + "".join([ ("<span class='"+i.css+"'>"+i.name+"</span>") for i in self.lines.all()]) 

    class Meta:
        ordering = ['name']

class Change(models.Model):
    at = models.ForeignKey('Station', on_delete=models.CASCADE, blank=False)
    from_direction = models.ManyToManyField('Direction', related_name='from_direction')
    to_direction = models.ManyToManyField('Direction', related_name='to_direction')
    waggon_choices = (
	(1, 'hinten'),
	(2, 'hinteres Drittel'),
	(3, 'mitte'),
	(4, 'vorderes Drittel'),
	(5, 'vorne'),
	(6, 'vorderes oder hinteres Drittel'),
	(7, 'egal'),
	(8, 'vorne oder hinten'),
	(9, 'vorderes Drittel oder mitte oder hinteres Drittel'),
	(10, 'vorderes Drittel oder vorne'),
	(11, 'hinteres Drittel oder hinten'),
    )
    waggon = models.PositiveSmallIntegerField( choices = waggon_choices )
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    comment = models.TextField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def waggon_template(self):
        return "umsteigen/waggon-" + str(self.waggon) + ".html"

    @property
    def direction_names(self):
        return " oder ".join([i.name for i in self.from_direction.all()])
    
    def __str__(self):
        return str(self.at) + ": " + ", ".join([str(i) for i in self.from_direction.all()]) + " ==to==> " + ", ".join([str(i) for i in self.to_direction.all()]) + ": " + str(self.waggon)

    class Meta:
        ordering = ['at']
