"""Conservative multibox carbon and two-layer heat emulator. Uncalibrated prototype."""
from dataclasses import dataclass,asdict
import math
@dataclass
class State:
 year:int=2025
 air:float=890.
 surface_ocean:float=900.
 deep_ocean:float=37100.
 vegetation:float=600.
 soil:float=1700.
 fossil:float=3500.
 surface_temp:float=1.2
 deep_temp:float=.35
 def carbon(self):return sum((self.air,self.surface_ocean,self.deep_ocean,self.vegetation,self.soil,self.fossil))
@dataclass(frozen=True)
class Parameters:
 air_ocean:float=.035
 ocean_mixing:float=.002
 photosynthesis:float=.018
 litter:float=.013
 respiration:float=.005
 land_use_gtc:float=1.1
 restoration_gtc:float=.2
 feedback:float=1.2
 heat_exchange:float=.7
 heat_surface:float=8.
 heat_deep:float=110.
def transfer(s,source,target,amount):
 if amount<0:return transfer(s,target,source,-amount)
 actual=min(amount,getattr(s,source))
 setattr(s,source,getattr(s,source)-actual)
 setattr(s,target,getattr(s,target)+actual)
 return actual
def step(previous,p,fossil_gtc=10.,land_use_gtc=None,extra_forcing=0.):
 if min(p.air_ocean,p.ocean_mixing,p.photosynthesis,p.litter,p.respiration,p.feedback,p.heat_exchange,p.heat_surface,p.heat_deep)<0 or p.heat_surface==0 or p.heat_deep==0:raise ValueError('invalid physical parameters')
 if fossil_gtc<0:raise ValueError('negative emissions')
 s=State(**asdict(previous));before=s.carbon()
 flux={}
 flux['fossil']=transfer(s,'fossil','air',fossil_gtc)
 lu=p.land_use_gtc if land_use_gtc is None else land_use_gtc
 flux['deforestation']=transfer(s,'vegetation','air',max(0,lu))
 flux['restoration']=transfer(s,'air','vegetation',p.restoration_gtc+max(0,-lu))
 flux['air_ocean']=transfer(s,'air','surface_ocean',p.air_ocean*((s.air-590)-(s.surface_ocean-900)))
 flux['ocean_mixing']=transfer(s,'surface_ocean','deep_ocean',p.ocean_mixing*((s.surface_ocean-900)-(s.deep_ocean-37100)))
 flux['photosynthesis']=transfer(s,'air','vegetation',p.photosynthesis*max(0,s.air-590))
 flux['litter']=transfer(s,'vegetation','soil',p.litter*max(0,s.vegetation-600))
 flux['respiration']=transfer(s,'soil','air',p.respiration*max(0,s.soil-1700)*(1+.04*max(0,s.surface_temp)))
 forcing=5.35*math.log(s.air/590)+extra_forcing
 a=1+(p.feedback+p.heat_exchange)/p.heat_surface
 b=-p.heat_exchange/p.heat_surface
 c=-p.heat_exchange/p.heat_deep
 d=1+p.heat_exchange/p.heat_deep
 det=a*d-b*c
 t1=s.surface_temp+forcing/p.heat_surface
 s.surface_temp=(d*t1-b*s.deep_temp)/det
 s.deep_temp=(-c*t1+a*s.deep_temp)/det
 s.year+=1
 if abs(s.carbon()-before)>1e-7:raise AssertionError('carbon conservation')
 if min(s.air,s.surface_ocean,s.deep_ocean,s.vegetation,s.soil,s.fossil)<0:raise AssertionError('negative carbon')
 return s,flux
