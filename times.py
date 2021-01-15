import glob
import os
import numpy as np
from astroplan import Observer
from astropy.time import Time
import astropy.units as u
from astropy.utils.iers import conf
conf.auto_max_age = None

now = Time.now()

date = '2020-12-05'
lco = Observer.at_site("lco")
#mmt = Observer.at_site('mmt', pressure=0*u.bar)

##'technical':['60.A-9700']
projects = ['chaname','brahm','moyano','zakhozhay','vines']
ids = {'chaname':['0106.A-9002'],'brahm':['0104.A-9007'],'zakhozhay':['0104.A-9003'],'moyano':['0106.A-9004'],'vines':['0106.A-9003']}

nights = {'moyano':['2020-12-28','2020-12-29'],\
		  'chaname':['2020-12-21','2020-12-22','2020-12-23','2020-12-24'],\
		  'zakhozhay':['2020-12-25','2020-12-26','2021-02-28','2021-03-01','2021-03-02','2021-03-03','2021-03-04','2021-03-05','2021-03-06','2021-03-07','2021-03-08','2021-03-09','2021-03-10','2021-03-11'],\
		  'brahm':['2020-12-03','2020-12-04','2020-12-05','2020-12-06','2020-12-07','2020-12-08','2020-12-09','2020-12-10','2020-12-11','2020-12-12',\
		           '2020-12-30','2020-12-31','2021-01-01','2021-01-02','2021-01-03','2021-01-04','2021-01-05','2021-01-06','2021-01-07','2021-01-08',\
		           '2021-02-17','2021-02-18','2021-02-19','2021-02-20','2021-02-21','2021-02-22','2021-02-23','2021-02-24','2021-02-25','2021-02-26','2021-02-27','2021-02-28'],\
		  'vines':['2021-03-28','2021-03-29','2021-03-30','2021-03-31']
		  }
used = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
full = {'chaname':0,'brahm':0,'zakhozhay':0,'moyano':0,'vines':0}
ratios=[]
available = 0.
date = Time(date+' 19:00')
while date < Time('2021-04-01 19:00'):

	tw1 = lco.twilight_evening_nautical(date, which='previous')
	tw2 = lco.twilight_morning_nautical(date, which='previous')
	ndur = float(str((tw2-tw1)*24.))


	for proj in projects:
		if str(date).split()[0] in nights[proj]:
			full[proj] += ndur
			if date > now:
				available += ndur 


	fil = 'nights/'+str(date).split()[0].replace('-','')+'.txt'
	if os.access(fil,os.F_OK):
		fle = open(fil,'r')
		flines = fle.readlines()
	else:
		flines = []
	tottime = 0
	for line in flines:
		cos = line.split()
		runID = cos[3]
		texp = cos[14]
		for proj in projects:
			pids = ids[proj]
			for pid in pids:
				if pid in runID:
					used[proj] += (float(texp)+240.)/3600.
					tottime += (float(texp) + 240.)/3600.
		#print(runID, texp)
		
	if len(flines)>0:
		ratios.append(tottime/ndur)

	##print(ndur,tottime/3600.)

	date += 1
ratios = np.array(ratios)

print('median efficiency ratio per night:',np.median(ratios))

print('used time per project:',used)

totfull= 0.
for proj in projects:
	full[proj] *= np.median(ratios)
	totfull += full[proj] 
available *= np.median(ratios)

props = {}
for proj in projects:
	props[proj] = full[proj]/totfull

print('Total time in semester per project:',full)
totused = 0
for proj in projects:
	totused+=used[proj]
print('total used time =', totused)
print('total available time =', available)
print('proportions =', props)

print('projected time left:')
for proj in projects:
	print(proj,props[proj]*(totused+available) - used[proj])


lines = ['# feros-pool\n', 'Computes used and available time for different observing projects\n']
lines.append('projected time left computed on '+str(now)+':\n')

for proj in projects:
	lines.append(' '+proj+': '+str(props[proj]*(totused+available) - used[proj])+' h \n')

ff = open('README.md','w')
for line in lines:
	ff.write(line)
ff.close()




