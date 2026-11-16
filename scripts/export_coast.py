"""Run with Blender -b La-cala-estados.blend -P export_coast.py -- OUTPUT_DIR."""
import bpy, os, sys, math, gzip, struct, json, random
from collections import defaultdict
from mathutils import Vector
from array import array
out=sys.argv[-1]
os.makedirs(out,exist_ok=True)
s=bpy.context.scene
ctrl=next(o for o in s.objects if o.name.startswith('00 •'))
types=['Umbrella pine 0','Umbrella pine 1','Umbrella pine 2','Lavender','Spanish sage','Feather grass','Daisies','Fine wild oat']
parts=['foundations','roof','walls','plumbing','garden']
batches=defaultdict(bytearray); plants=[]; treesizes=[]
def driver_part(o):
 for f in (o.animation_data.drivers if o.animation_data else []):
  for v in f.driver.variables:
   p=v.targets[0].data_path
   if p.startswith('["'):return p[2:-2]
def category(o):
 n=o.name.lower()
 if n.startswith(('zinc flue','flue collar','standing seam','folded standing','parapet','coping','cubierta')):return 'roof'
 if any(k in n for k in ['pool','ripple','mosaic','piscina','ladder']):return 'plumbing'
 if n.startswith(('cimentación','approach paving','floating entrance','hand laid fieldstone','terrace cut')):return 'foundations'
 if n.startswith(('jardín','pot foliage','earthenware','garden limestone')):return 'garden'
 return 'walls'
def score(p):
 for k in parts:ctrl[k]=float(p)
 ctrl.update_tag();bpy.context.view_layer.update()
score(94)
objs=list(s.objects)
for o in objs:
 if o.type=='MESH' and o.data.name in types and abs(o.location.x)<55:
  part=driver_part(o)
  states=[]
  if part:
   expr=o.animation_data.drivers[0].driver.expression
   states=['solid'] if '70' in expr else ['solid','cracked']
  plants.append([types.index(o.data.name),*[round(float(a),3) for a in o.location],round(o.scale.x,3),states])
# Sample local coordinates at 5 mm precision. A face carries its evaluated Blender finish and normal.
point=struct.Struct('<hhhbbbBBB')
def byte(x):return max(0,min(255,round(255*x)))
def lin(v):return 12.92*v if v<.00313 else 1.055*v**(1/2.4)-.055
# Bake ambient contact shadows in linear colour. The browser can then retain
# depth around reveals and furniture even when dynamic shadows are disabled.
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bv=[];bf=[]
for o in objs:
 if o.type!='MESH' or abs(o.location.x)>21 or o.data.name in types or o.hide_render:continue
 if len(o.data.vertices)>2000 or o.name.startswith(('Lluvia','Garden limestone','Pot foliage','Mosaic joint')):continue
 if any(slot.material and ('glazing' in slot.material.name.lower() or 'rippling' in slot.material.name.lower()) for slot in o.material_slots):continue
 base=len(bv);bv.extend(o.matrix_world@v.co for v in o.data.vertices)
 bf.extend(tuple(base+i for i in face.vertices) for face in o.data.polygons)
tree=BVHTree.FromPolygons(bv,bf)
cache={}
def shade(pos,n):
 key=tuple(round(c/10) for c in pos)+tuple(round(c/13) for c in n)
 if key in cache:return cache[key]
 origin=Vector(pos)/200;axis=Vector(n).normalized()
 tangent=axis.cross(Vector((0,0,1)) if abs(axis.z)<.9 else Vector((1,0,0))).normalized()
 up=axis.cross(tangent);amount=0
 for i in range(9):
  angle=i*2.39996;vertical=.18+.78*i/8;spread=math.sqrt(1-vertical*vertical)
  direction=axis*vertical+(tangent*math.cos(angle)+up*math.sin(angle))*spread
  _,_,_,dist=tree.ray_cast(origin+axis*.035,direction,2.8)
  if dist is not None:amount+=(1-dist/2.8)
 cache[key]=1-.60*amount/9
 return cache[key]
def write_obj(o,part,tag,dg):
 oe=o.evaluated_get(dg)
 if oe.hide_render:return
 me=oe.to_mesh()
 if me is None:return
 me.calc_loop_triangles();world=oe.matrix_world;normal=world.to_3x3().inverted_safe().transposed()
 mats=[]
 for m in me.materials:
  name=m.name.lower() if m else ''
  finish='glass' if 'glazing' in name else 'water' if 'rippling' in name else 'lamp' if 'light' in name else 'metal' if any(w in name for w in ['zinc','bronze']) else 'stone'
  c=m.diffuse_color[:3] if m else (.5,.5,.5)
  mats.append((finish,[byte(lin(x)) for x in c]))
 pos=[tuple(max(-32767,min(32767,round(x*200))) for x in world@v.co) for v in me.vertices]
 for tri in me.loop_triangles:
  finish,c=mats[tri.material_index] if mats else ('stone',[180]*3)
  norm=[round(x*127) for x in (normal@tri.normal).normalized()]
  buf=batches[(part,tag,finish)]
  for i in tri.vertices:
   ao=shade(pos[i],norm) if finish not in ('glass','water','lamp') else 1
   buf.extend(point.pack(*pos[i],*norm,*[round(v*ao) for v in c]))
 oe.to_mesh_clear()
for val,state in [(94,'solid'),(55,'cracked'),(18,'broken')]:
 score(val);dg=bpy.context.evaluated_depsgraph_get()
 for o in objs:
  if o.type not in ['CURVE','MESH'] or abs(o.location.x)>75:continue
  if o.name.startswith(('Botanical planting','Lluvia','Coastal mountain','Bay','Natural coastal','Garden limestone','Mosaic joint')) or (o.type=='MESH' and o.data.name in types):continue
  k=driver_part(o)
  if k=='global' or (not k and state!='solid'):continue
  write_obj(o,k or category(o),state if k else 'always',dg)
# Use the original sculpted terrain with its pool opening and a coarser sampling grid beyond the terrace.
from mathutils import noise
def ground(x,y):
 t=max(abs(x)/14,abs(y)/11)
 return -.018-min(9,max(0,t-1)*2.6)+min(1,max(0,t-1))*noise.fractal(Vector((x*.077,y*.077,.13)),1.1,2,3)
xs=sorted(set(list(range(-50,51,2))+[2.92,8.68]));ys=sorted(set(list(range(-44,51,2))+[-7.21,-4.19]))
for a,b in zip(xs,xs[1:]):
 for e,f in zip(ys,ys[1:]):
  if 2.92<(a+b)/2<8.68 and -7.21<(e+f)/2<-4.19:continue
  for x,y in [(a,e),(b,e),(b,f),(a,e),(b,f),(a,f)]:
   z=ground(x,y);tone=.92+.08*math.sin(x*.47+y*.31)
   batches[('land','always','earth')].extend(point.pack(round(x*200),round(y*200),round(z*200),0,0,127,*[int(tone*c) for c in (182,170,136)]))
# Local olive trees share the grove foliage atlas at a smaller scale.
for x,y,h in [(-8.85,2.8,4.15),(-8.45,-4.05,3.32),(8.65,4.86,4.2),(1.15,6.32,3.7)]:
 plants.append([0,x,y,0,h/8,['olive']])
meta=[];binary=bytearray()
for (p,state,m),buf in batches.items():
 meta.append([p,state,m,len(buf)//point.size]);binary.extend(buf)
with gzip.open(os.path.join(out,'villa.bin.gz'),'wb',compresslevel=7) as f:f.write(binary)
# Bake real cutouts of the linked Blender plant meshes for the interactive garden.
atlas=bpy.data.scenes.new('Foliage cutouts');atlas.world=bpy.data.worlds.new('Soft daylight');atlas.world.color=(.62,.68,.74)
atlas.render.engine='CYCLES';atlas.cycles.samples=8;atlas.render.film_transparent=True;atlas.cycles.transparent_max_bounces=3
atlas.render.resolution_x=384;atlas.render.resolution_y=384;atlas.render.resolution_percentage=100;atlas.render.image_settings.file_format='PNG'
camera=bpy.data.cameras.new('Plant elevation');eye=bpy.data.objects.new('Plant elevation',camera);atlas.collection.objects.link(eye);atlas.camera=eye;camera.type='ORTHO'
ld=bpy.data.lights.new('Key','SUN');ld.energy=3.5;light=bpy.data.objects.new('Key',ld);atlas.collection.objects.link(light);light.rotation_euler=(.55,-.64,-.3)
for i,name in enumerate(types):
 ob=bpy.data.objects.new('Cutout',bpy.data.meshes[name]);atlas.collection.objects.link(ob)
 zs=[v.co.z for v in ob.data.vertices];lo=min(zs);hi=max(zs)
 size=max(hi-lo, max(abs(v.co.x) for v in ob.data.vertices)*2)*1.04;camera.ortho_scale=size
 eye.location=(0,-24,(lo+hi)/2);eye.rotation_euler=(math.pi/2,0,0)
 treesizes.append([round(size,4),round((lo+hi)/2,4)])
 atlas.render.filepath=os.path.join(out,'plant-%s.png'%i);bpy.ops.render.render(scene=atlas.name,write_still=True);bpy.data.objects.remove(ob,do_unlink=True)
with open(os.path.join(out,'villa.json'),'w') as f:json.dump({'batches':meta,'plants':plants,'sizes':treesizes},f,separators=(',',':'))

