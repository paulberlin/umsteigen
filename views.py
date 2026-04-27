from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from django.core.mail import send_mail
from django.contrib import messages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.db.models import Count

from .models import Line
from .models import Direction
from .models import Station
from .models import Change

from .forms import AddChange


def index(request):
    line_counter = Line.objects.all().count()
    station_counter = Station.objects.all().count()
    station_complete_counter = Station.objects.filter(complete=True).count()
    change_counter = Change.objects.all().count()
    station_list = Station.objects.filter(change_station=True)
    last_modified = Change.objects.all().order_by('-updated_at')[0]
    contributions = (Change.objects.values('name').annotate(dcount=Count('name')).order_by()).order_by('-dcount')[0:10]
    context = { 'line_counter': line_counter, 'station_counter': station_counter, 'station_complete_counter': station_complete_counter, 'change_counter': change_counter, 'station_list': station_list, 'last_modified': last_modified, 'contributions': contributions }
    return render(request, 'umsteigen/index.html', context)

def contact(request):
    line_counter = Line.objects.all().count()
    station_counter = Station.objects.all().count()
    change_counter = Change.objects.all().count()
    station_list = Station.objects.filter(change_station=True)
    context = { 'line_counter': line_counter, 'station_counter': station_counter, 'change_counter': change_counter, 'station_list': station_list }
    return render(request, 'umsteigen/contact.html', context)

def privacy(request):
    context = { }
    return render(request, 'umsteigen/privacy.html', context)

def stats(request):
    line_counter = Line.objects.all().count()
    station_counter = Station.objects.all().count()
    change_counter = Change.objects.all().count()
    station_list = Station.objects.filter(change_station=True)
    context = { 'line_counter': line_counter, 'station_counter': station_counter, 'change_counter': change_counter, 'station_list': station_list }
    return render(request, 'umsteigen/stats.html', context)

def line_list(request):
    line_list = Line.objects.all()
    station_list = Station.objects.filter(change_station=True)
    context = { 'line_list': line_list, 'station_list': station_list }
    return render(request, 'umsteigen/line_list.html', context)

def line_detail_name(request, urlname):
    if len(urlname) >= 2:
      print("urlname: " + urlname)
      linetype = urlname[0:1]
      numb = urlname[1:]
      print("type: " + linetype)
      print("numb: " + str(numb))
      line = get_object_or_404(Line, line_type=linetype.lower(), number=int(numb))
      print("line: " + line.name)
      print("line_detail_name")
      print("line: " + line)
      return line_detail(request, line.line_id)
    return index(request)

def line_detail(request, id, sequence=False):
    print("line_detail start")
    line = get_object_or_404(Line, pk=id)
    station_list = Station.objects.filter(change_station=True)
    line_station_list = station_list
    tab_alpha = ''
    tab_sequence = ''
    if sequence:
      line_station_list = Station.objects.filter(lines__exact=id).order_by('sequence')
      tab_sequence = 'active'
    else:
      line_station_list = Station.objects.filter(lines__exact=id)
      tab_alpha = 'active'
    context = { 'line': line, 'line_station_list': line_station_list, 'station_list': station_list, 'tab_alpha': tab_alpha, 'tab_sequence': tab_sequence, 'sequence': sequence }
    print ("end view")
    return render(request, 'umsteigen/line_detail.html', context)

def station_list(request):
    station_list = Station.objects.filter(change_station=True)
    context = { 'station_list': station_list }
    return render(request, 'umsteigen/station_list.html', context)

def station_detail(request, id):
    station = get_object_or_404(Station, pk=id)
    change_list = Change.objects.filter(at__exact=id)
    thanks_list = Change.objects.filter(at__exact=id).exclude(name='').exclude(name__isnull=True).values('name').distinct().order_by('name')
    station_list = Station.objects.filter(change_station=True)
    context = { 'station': station, 'change_list': change_list, 'thanks_list': thanks_list, 'station_list': station_list, "authenticated": request.user.is_authenticated }
    return render(request, 'umsteigen/station_detail.html', context)

def station_detail_name(request, urlname):
    station = get_object_or_404(Station, url_name=urlname)
    return station_detail(request, station.station_id)

def station_add_change(request, id):
    #print("add_change:" + str(id))
    station = get_object_or_404(Station, pk=id)
    form = AddChange(station, initial={'at': station.station_id})
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddChange(station, request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            # send email
            message = '''
            name: %s
            station: %s
            link: https://umsteigen-in-berlin.de/app/station/%s
            ''' % (form.cleaned_data.get('name'), form.cleaned_data.get('at'), id )
            msg = MIMEMultipart()
            msg['From'] = settings.SERVER_EMAIL
            msg['To'] = 'paul.fuehring@gmx.net' #settings.MANAGERS[0]
            msg['Subject'] = 'Neuer Umsteigen Input'
            msg.attach(MIMEText(message))
            mailserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_HOST_PORT)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.ehlo()
            mailserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            mailserver.sendmail(settings.SERVER_EMAIL, 'paul.fuehring@gmx.net', msg.as_string())
            mailserver.quit()

            #send_mail(
            #    'Neuer Umsteigen-Input',
            #    'Von: ' + form.cleaned_data.get('name'),
            #    'umstieg@uber.space',
            #    ['paul.fuehring@gmx.net'],
            #    fail_silently=False,
            #)
            messages.success(request, 'Danke für Deinen Hinweis!')
            return redirect('station_detail_name', station.url_name)

        # if a GET (or any other method) we'll create a blank form
        else:
            form = Addchange()

    context = { 'station': station, 'form': form }
    return render(request, 'umsteigen/station_add_change.html', context)


