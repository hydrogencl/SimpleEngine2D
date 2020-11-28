import pygame
import math,re
import random

####--------------------------------------------------------------#### 
# Version 0.98: Need to add AI for missile or enemy                  #
#             :    - Add/appoint specific obj for AI                 # 
#             :    - Add AI scheme                                   # 
#             : Need to add plasma effect                            # 
#             : Need to add explosive effect                         # 
# 19.07.20 : Changing the loop algorithm                             # 
# 22.03.20 : Adding AI                                               #
# 14.08.19 : DONE DEBUGGING the collision reaction                   # 
# 30.07.19 : Changing the scheme of velocity in  X-direction         # 
# 05.06.19 : Fixing Tilt velocity and tilt direction indicator in    #
#            the angle array                                         #
# 19.05.19 : Done physic reaction, changing tilt from velocity to    #
#            power based                                             # 
#            Problem: wrong collision                                #
# 24.03.19 : doing physics reactions ... cannot call object reaction?#
# 22.01.19 : should change to physical behaviour                     #
# 08.01.19 : should put all objects in the array                     #
#            DONE!                                                   #
# 18.12.18 : Checking solving problems                               #
# 0923: 1. solving the camera: now can free to move with fix camera  # 
# 1.  Need to add the global coordination system                     #
# 2.  Need to add the Missile function                               #
# 3.1 Need to add the AI for Missile                                 #
# 4.  Need to add the AI for enemy                                   #
# 7.  Need to add the explosion effect (vectorize beam, debris)      #
#                                                                    #
# "Sound effects obtained from https://www.zapsplat.com"             #
####--------------------------------------------------------------####

#------------------------------------#
#        MATH TOOL                   # 
#------------------------------------#

def ratio(num_in1, num_in2, num_ratio):
    return (num_in1 - (num_in1 - num_in2)*num_ratio)

def a_sin(angle): return math.sin(angle/180.0*math.pi)
def a_cos(angle): return math.cos(angle/180.0*math.pi)

def num_C2P(arr_in1, arr_in2):
    # changing X-Y(Cartesian) coordination system to polar 
    num_length = ((arr_in1[0] - arr_in2[0])**2 + (arr_in1[1] - arr_in2[1])**2) ** 0.5
    if arr_in1[1] - arr_in2[1] == 0 and arr_in1[0] > arr_in2[0]:
        num_phi =  90.0
    elif arr_in1[1] - arr_in2[1] == 0 and arr_in1[0] < arr_in2[0]:
        num_phi =  270.0
    elif arr_in1[0] - arr_in2[0] == 0:
        num_phi = 0.0
    else:
        num_phi    = math.atan(float(arr_in1[0] - arr_in2[0])/(arr_in1[1] - arr_in2[1])) * 180.0 / math.pi
    if arr_in1[1] >= arr_in2[1]:
        return num_length, num_phi 
    elif arr_in1[1] < arr_in2[1]:
        return num_length, num_phi+180

# ------------------------------------ #
#                OBJECTS               # 
# ------------------------------------ #

class MotionObject:
    """
    An object, with hit point, velocity, components
    PS: arr_body is in normal coordination, not pygame, which is upside-down  
    """  

    str_ID                 = ""
    arr_pos                = [0,0]

    arr_body             = [[0,11],[1,8],[3,7],[3,8],[4,6.5],[6,5],[2,2],[1,1],[0,2],[-1,1],[-2,2],[-6,5],[-4,6.5],[-3,8],[-3,7],[-1,8]]
    arr_color            = (255,255,255)
    arr_gun_point    = [[-3,8],[3,8],[4,6.5],[-4,6.5]] 
    arr_missile_point= [[2,5],[-2,5]]
    arr_engine_point = [[-1,1],[1,1]] 

    arr_fire_point   = [[] for n in range(len(arr_gun_point))] 
    arr_plasma_point = [[] for n in range(len(arr_engine_point))] 
    if_exist             = True 

    num_scale            =  1   
    arr_hit_center       =  [0.0 , 6]
    num_hit_range        =  5
    arr_shield_center    =  [0.0 , 6]
    num_shield_range     =  7
    
    # Control-Move
    if_forward         = False
    if_reverse         = False
    if_tilt_r            = False
    if_tilt_l            = False 

    # Weapon System
    num_missile         = 6
    num_laser_EP        = 2 
    #dic_fire_cd         = {"laser":[True,300,0], "ion":[True,500,0], "missile":[True, 1000, 0]}
    param_weapon  = {"name"             : ["laser",  "ion","aa-msl"],\
                           "lasttime"     : [    100,    100,     200],\
                           "speed"        : [     30,     20,      10],\
                           "if_fire"      : [   True,   True,    True],\
                           "num_EP"       : [      1,      2,       0],\
                           "arr_color"    : [(250,  0,  0), (  0,250,  0),(250,250,250)],\
                           "arr_shape"    : [[[0,3],[0,0],[0,3]], [[0,3],[0,0],[0,3]], [[0,0],[0,3],[0.5,3.5],[0,4],[-0.5,3.5],[0,3],[0,0]],(250,250,250)],\
                           "num_cd_time"  : [    100,    300,     500],\
                           "num_cd_count" : [      0,      0,       0],\
                           "num_HP_damage": [     30,      5,     100],\
                           "num_SH_damage": [     10,    100,     100],\
                           "num_EP_damage": [      0,    100,       0]}
    # Locking system
    num_scan_angle     = 15     # +- degree
    num_scan_in_dist   = 1000
    num_scan_out_dist  = 1800
    num_lock_ID            = 4
    arr_lock_tg_ID     = [[0,[]] for n in range(num_lock_ID)]
        
    arr_missile         = []

    param_ai       = {"Detect_Radius"  : 200   ,\
	              "Moving_Pattern" : "line",\
	              "Moving_Radius"  : 600   ,\
    }

    # Input Parameters
    def __init__(self,  arr_pos, num_rotation, str_ID="", num_hp=1, num_ep=1, num_sh=1):
        # ALL local variables
        self.MAX_HP  = num_hp
        self.MAX_EP  = num_ep
        self.MAX_SH  = num_sh
        self.HP      = num_hp
        self.EP      = num_ep
        self.SH      = num_sh
        self.arr_pos    = arr_pos                   # [ X , Y ]
        self.num_angle = [num_rotation, 0.0]            # + : clockwise
        self.str_ID     = str_ID

        self.num_angle             =  [0.0, 0.0]
        self.num_angle_speed     =  0
        self.num_angle_rate      =  0.1
        self.num_max_angle_speed =  2

        self.num_tilt             =  0.0
        self.num_max_tilt         =  45  # Degree
        self.num_max_velocity     =  10  # 
        self.num_tilt_speed       =  0.1
        self.num_max_tilt_speed   =  0.1
        self.num_ff_velocity      =  0.0
        self.num_acceleration     =  0.1
        self.num_tilt_speed_scale =  0.1

        # Physical response
        self.arr_force                = [0.0,  0.0]              # final force [X,Y]
        self.arr_forces             = [[0.0, 0.0],[0.0, 0.0]]  # all force components([[Internal], [External]])
        self.arr_velocity         = [0.0,  0.0]                  # final velocity for calculating the position
                                                                 # V1=X along object, V2=Y along object
        self.num_mass                 = 1.0
        self.arr_velo_dir         = [0.0, 0.0]
        # Engine Characteristic
        self.arr_force_scale      = [0,0,  0,0] # Force provided by Engine
        self.arr_force_power      = [1.0,  0.8,  1.0] # scale of power, [Y, -Y, +-X]

    def fire_weapon(self, if_fire=False, num_game_time=0):
        # Based on a signal model: input-signal -> firing-signal 
        #                               -> check the cool-down time
        num_wea = len(self.param_weapon["name"])
        arr_if_signal =[ False for n in range(num_wea)]
        for w in range(num_wea):
            if self.EP  == 0:
                self.param_weapon["if_fire"][w] = False

            if if_fire == True and self.param_weapon["if_fire"][w] == True:
                arr_if_signal[w] = True
                self.EP -= self.param_weapon["num_EP"][w]

            if self.EP >= 0:
                  if arr_if_signal[w] == True:
                      self.param_weapon["num_cd_count"][w] = num_game_time

            num_gun = len(self.arr_gun_point)
            self.EP = min(self.MAX_EP,max(0,self.EP))
            
            for n_g in range(num_gun):
                num_length, num_phi  = num_C2P(self.arr_gun_point[n_g],[0,0])
                self.arr_fire_point[n_g] = [self.arr_pos[0] + num_length*a_sin(num_phi+self.num_angle[0])*self.num_scale, self.arr_pos[1] + num_length*a_cos(num_phi+self.num_angle[0])*self.num_scale  ] 

    def locking_system(self):
        return 0

    def add_missile(self, arr_pos, str_purpose):
        if len(self.arr_missile) < self.num_missile:
            self.arr_missile.append([arr_pos, str_purpose])
        self.EP += 100
    
    def power_system(self, if_forward, if_reverse, if_power):
        # This power system is depend on F=ma
        self.num_force_dir = 1.0
        if if_forward: 
            self.arr_force_scale[1]   +=   1.0 * self.arr_force_power[0]
            num_force_dir = 1.0
        if if_reverse:
            self.arr_force_scale[1]   +=  -1.0 * self.arr_force_power[1]
            num_force_dir = -1.0
        if not if_power:
            #if self.arr_force_scale[1] > 2.05:
            #    self.arr_force_scale[1] -=  self.arr_force_power[0]
            #elif self.arr_force_scale[1] < -2.05:
            #    self.arr_force_scale[1] +=  self.arr_force_power[1]
            #else:
            self.arr_force_scale[1] = 0 
            num_force_dir =  0.0
        self.arr_forces[0][1] = num_force_dir * abs(self.arr_force_scale[1])
        #print("force scale", self.str_ID, self.arr_force_scale, num_force_dir)
        num_engine = len(self.arr_engine_point)
        for n_e in range(num_engine):
                num_length, num_phi  = num_C2P(self.arr_gun_point[n_e],[0,0])
                self.arr_plasma_point[n_e] = [self.arr_pos[0] + num_length*a_sin(num_phi+self.num_angle[0])*self.num_scale, self.arr_pos[1] + num_length*a_cos(num_phi+self.num_angle[0])*self.num_scale  ] 
    
    def tilt_system(self, if_forward, if_reverse, if_power):
        # This power system is depend on F=ma
        if if_forward: 
            self.arr_force_scale[0]   +=   1.0 * self.arr_force_power[0]
            self.num_angle[1] = 0
            self.num_tilt += self.num_tilt_speed  #* self.arr_force_power[0]
        elif if_reverse:
            self.arr_force_scale[0]   +=  -1.0 * self.arr_force_power[0]
            self.num_angle[1] = 180
            self.num_tilt -= self.num_tilt_speed  #* self.arr_force_power[0]
	self.num_tilt = max(self.num_tilt, -1*self.num_max_tilt)
        if not if_power:
            self.arr_force_scale[0] = 0 
            self.num_angle[1] =   0
            if self.num_tilt > 1.0: 
                self.num_tilt -= a_cos(self.num_angle[1]) 
            elif self.num_tilt < -1.0: 
                self.num_tilt += a_cos(self.num_angle[1]) 
            else: 
                self.num_tilt = 0 

        self.num_force_dir = a_cos(self.num_angle[1])
        self.arr_forces[0][0] = self.num_force_dir * abs(self.arr_force_scale[0])

    def self_physics(self, num_time_interval=0.1, if_drag_force=True):
        self.arr_force = [0,0]
        if self.arr_velocity[0] > 0:
            self.arr_velo_dir[0] = 1
            self.num_angle[1] = 0
        elif self.arr_velocity[0] < 0:
            self.arr_velo_dir[0] = -1
            self.num_angle[1] = 180
        if self.arr_velocity[1] > 0:
            self.arr_velo_dir[1] = 1
        elif self.arr_velocity[1] < 0:
            self.arr_velo_dir[1] = -1

        if if_drag_force:
            self.arr_forces[1][0] = drag_force(self.arr_velocity[0]) * self.arr_velo_dir[0]
            self.arr_forces[1][1] = drag_force(self.arr_velocity[1]) * self.arr_velo_dir[1]

        for n in range(len(self.arr_forces)):
            self.arr_force[0] += self.arr_forces[n][0]
            self.arr_force[1] += self.arr_forces[n][1]

        self.num_acc_x        = self.arr_force[0] / self.num_mass
        self.num_acc_y        = self.arr_force[1] / self.num_mass
        self.arr_velocity[0] += 0.5 * self.num_acc_x * (num_time_interval) ** 2
        self.arr_velocity[1] += 0.5 * self.num_acc_y * (num_time_interval) ** 2
        if self.arr_velocity[1] < 0.05 and self.arr_velocity[1] > -0.05: self.arr_velocity[1] = 0
        if self.arr_velocity[0] < 0.05 and self.arr_velocity[0] > -0.05: self.arr_velocity[0] = 0
        self.arr_velocity[0] = min(self.arr_velocity[0], self.num_max_velocity)
        self.arr_velocity[1] = min(self.arr_velocity[1], self.num_max_velocity)
        self.arr_pos[0] += self.arr_velocity[1] * a_sin(self.num_angle[0])
        self.arr_pos[1] += self.arr_velocity[1] * a_cos(self.num_angle[0])
        self.arr_pos[0] += self.arr_velocity[0] * a_sin(self.num_angle[0]+90 )
        self.arr_pos[1] += self.arr_velocity[0] * a_cos(self.num_angle[0]+90 )

    def power_system_vel(self, if_forward, if_reverse, if_power):
        # this is a very comfortable moving method I made
        if if_forward: 
            self.num_ff_velocity += 1.0 * self.num_acceleration 
            self.num_ff_velocity = min(self.num_ff_velocity, 1.0 * self.num_max_velocity)
        if if_reverse:
            self.num_ff_velocity += -1.0 * self.num_acceleration
            self.num_ff_velocity = max(self.num_ff_velocity, -1.0 * self.num_max_velocity)
        if not if_power:
            if self.num_ff_velocity > 0.05:
                self.num_ff_velocity += -1.0 * self.num_acceleration
            elif self.num_ff_velocity < -0.05:
                self.num_ff_velocity += 1.0 * self.num_acceleration
            else:
                self.num_ff_velocity = 0.0 
        #print if_forward, if_reverse, self.num_ff_velocity
        self.arr_pos[0] += self.num_ff_velocity * a_sin(self.num_angle[0])
        self.arr_pos[1] += self.num_ff_velocity * a_cos(self.num_angle[0])

        num_engine = len(self.arr_engine_point)
        for n_e in range(num_engine):
            num_length, num_phi  = num_C2P(self.arr_gun_point[n_e],[0,0])
            self.arr_plasma_point[n_e] = [self.arr_pos[0] + num_length*a_sin(num_phi+self.num_angle[0])*self.num_scale, self.arr_pos[1] + num_length*a_cos(num_phi+self.num_angle[0])*self.num_scale  ] 

    def turn_system(self, if_turn_right, if_turn_left):
        if if_turn_right:
            num_angle_direction =  1 
            self.num_angle_speed += self.num_angle_rate * num_angle_direction
        elif if_turn_left: 
            num_angle_direction = -1
            self.num_angle_speed += self.num_angle_rate * num_angle_direction
        else:
            if self.num_angle_speed > 0:
                num_angle_direction =  -1
            elif self.num_angle_speed <0:
                num_angle_direction =   1
            else:
                num_angle_direction =   0
            self.num_angle_speed += self.num_angle_rate * num_angle_direction
            if abs(self.num_angle_speed) <0.5:
                self.num_angle_speed = 0
        self.num_angle_speed  = min(self.num_max_angle_speed, self.num_angle_speed)
        self.num_angle_speed  = max(self.num_max_angle_speed*-1, self.num_angle_speed)
        self.num_angle[0] += self.num_angle_speed


class UncontrolObject:
    arr_pos                = [0,0]
    num_angle            = 0.0
    num_velocity     = 0
    num_last_time    = 0
    if_exist             = True 
    # Because the UncontrolObject is most of weapon bullets, there is number for damage
    num_HP_dmg         = 0
    num_SH_dmg         = 0
    num_EP_dmg         = 0
    arr_shape            = []
    arr_color            = [255,255,255]
    num_angle_speed = 1.0

    def __init__(self, arr_pos, num_angle, num_velocity, num_last_time, arr_color, arr_shape,arr_dmg=[0,0,0]):
        self.arr_pos       = arr_pos
        self.num_angle     = num_angle
        self.num_velocity  = num_velocity
        self.num_last_time = num_last_time
        self.num_HP_dmg    = arr_dmg[0]
        self.num_SH_dmg    = arr_dmg[1]
        self.num_EP_dmg    = arr_dmg[2]
        self.arr_shape     = arr_shape 
        self.arr_color     = arr_color 
        
    def cal_time(self, num_dis_rate=1):
        if self.num_last_time > 0:
            self.num_last_time -= num_dis_rate 
        if self.num_last_time <= 0:
            self.if_exist = False

    def cal_position(self):
        self.arr_pos[0] += self.num_velocity * a_sin(self.num_angle)
        self.arr_pos[1] += self.num_velocity * a_cos(self.num_angle)

    def missile(self, arr_tg_pos):
        num_rl_dist, num_rl_angle = num_C2P(self.arr_pos, arr_tg_pos)

        velocity = 0
        num_dist = 0
        self.arr_pos[0] += self.num_velocity * a_sin(num_angle)
        self.arr_pos[1] += self.num_velocity * a_cos(num_angle)
        if num_rl_angle > 0.05: 
            self.num_angle -= self.num_angle_speed
        elif num_rl_angle < 0.05: 
            self.num_angle += self.num_angle_speed
        else:
            pass
        
    
class EffectObject:
    """
    This is an object for dealing with effects. 
    The effect may move or not. 
    Three effects are employed now:
    1) shield_blink: draw circles
    2) explosion   : lines (sparks) and debris fly away
    3) sparks        : just some sparks by hitting
    4) jet stream  : jet/plasma stream
    """
    arr_pos        = [0,0]
    num_angle    = 0.0
    str_effect   = ""

    if_exist     = True

    def __init__(self, arr_position, num_angle, var_screen):
        self.arr_pos    = arr_position 
        self.num_angle  = num_angle
        self.str_effect = ""
        var_screen      = ""
        return 0    

    def Motion(self, str_motion="Still", num_velocity=0, arr_update_pos=[0,0]):
        if str_motion   == "Still":
            pass
        elif str_motion == "Along":
            self.arr_pos[0] += num_velocity*a_sin(self.num_angle)
            self.arr_pos[1] += num_velocity*a_cos(self.num_angle)
        elif str_motion == "followObject":
            self.arr_pos = arr_update_pos
        else:
            print("ERROR: Do not setup the motion method")
    def shield_blink(self):

        return 0    
    
    def explosion(self):
        return 0    
    
    def sparks(self):
        return 0    

    def jet_stream(self, arr_jet_point, num_angle):
    
      math.sin(arr_x[n]) * math.e**(-1*arr_x[n])
      return 0    

#------------------------------------#
#             CAMERA                 # 
#------------------------------------#

class Camera:
  """
  all the information used for camera
  follow_object: camera fix with object
  go_to_target : camera will go to the target object

  """
  arr_camera_xy = []
  arr_screen_size = [] 
  Camera_parameter = {"num_Xsta"     : 0, \
                      "num_Xend"     : 0, \
                      "num_Ysta"     : 0, \
                      "num_Yend"     : 0, \
                      "num_Angle"    : 0, \
                      "arr_center"      : [0,0],\
                      "arr_screen_size" : [0,0]} 

  arr_obj_pos   = []
  num_obj_angle = 0.0

  def __init__(self, arr_screen_size=[]):
    self.Camera_parameter["num_Xsta"]  = 0
    self.Camera_parameter["num_Xend"]  = arr_screen_size[0]
    self.Camera_parameter["num_Ysta"]  = 0
    self.Camera_parameter["num_Yend"]  = arr_screen_size[1]
    self.arr_screen_size = arr_screen_size
    self.Camera_parameter["arr_center"] = [0.5*arr_screen_size[0], 0.5 * arr_screen_size[1]]
    self.Camera_parameter["arr_screen_size"] = arr_screen_size

  def changing_camera_pos(self, arr_move):

    self.Camera_parameter["num_Xsta"] = 0 + arr_move[0]
    self.Camera_parameter["num_Xend"] = arr_screen_size[0] + arr_move[0]
    self.Camera_parameter["num_Ysta"] = 0 + arr_move[1]
    self.Camera_parameter["num_Yend"] = arr_screen_size[1] + arr_move[1]
    return self.Camera_parameter 

  def follow_object_rotate(self, arr_obj_os_pos, arr_obj_sys_pos, num_obj_angle):
    # os: on screen ; sys: "real" in the game

    self.Camera_parameter["Camera_angle"]  = num_obj_angle 

    num_Xsta_t = arr_obj_sys_pos[0] - arr_obj_os_pos[0] 
    num_Xend_t = self.arr_screen_size[0]- arr_obj_os_pos[0] + arr_obj_sys_pos[0]
    num_Ysta_t = arr_obj_sys_pos[1] - arr_obj_os_pos[1]  
    num_Yend_t = self.arr_screen_size[1]- arr_obj_os_pos[1] + arr_obj_sys_pos[1]

    arr_X0Y0 = [num_Xsta_t, num_Ysta_t ]
    arr_X1Y1 = [num_Xend_t, num_Yend_t ]
    arr_C2P_X0Y0 = num_C2P(arr_X0Y0, arr_obj_os_pos)
    arr_C2P_X1Y1 = num_C2P(arr_X1Y1, arr_obj_os_pos)

    self.Camera_parameter["num_Xsta"]  = arr_C2P_X0Y0[0] * a_sin(arr_C2P_X0Y0[1] - num_obj_angle)
    self.Camera_parameter["num_Xend"]  = arr_C2P_X1Y1[0] * a_sin(arr_C2P_X1Y1[1] - num_obj_angle)
    self.Camera_parameter["num_Ysta"]  = arr_C2P_X0Y0[0] * a_cos(arr_C2P_X0Y0[1] - num_obj_angle)
    self.Camera_parameter["num_Yend"]  = arr_C2P_X1Y1[0] * a_cos(arr_C2P_X1Y1[1] - num_obj_angle)

    self.Camera_parameter["arr_center"]    = arr_obj_sys_pos
    return self.Camera_parameter

  def follow_object(self, arr_obj_os_pos, arr_obj_sys_pos, num_obj_angle):
    # os: on screen ; sys: "real" in the game
    self.Camera_parameter["Camera_angle"]  = num_obj_angle 
    self.Camera_parameter["num_Xsta"]      = 0 - arr_obj_os_pos[0] + arr_obj_sys_pos[0] 
    self.Camera_parameter["num_Xend"]      = self.arr_screen_size[0]- arr_obj_os_pos[0] + arr_obj_sys_pos[0]  
    self.Camera_parameter["num_Ysta"]      = 0 - arr_obj_os_pos[1] + arr_obj_sys_pos[1] 
    self.Camera_parameter["num_Yend"]      = self.arr_screen_size[1]- arr_obj_os_pos[1] + arr_obj_sys_pos[1]
    self.Camera_parameter["arr_center"]    = [arr_obj_os_pos[0] + self.Camera_parameter["num_Xsta"] \
                                             ,arr_obj_os_pos[1] + self.Camera_parameter["num_Ysta"]]
    return self.Camera_parameter

  def go_to_target(self, arr_target_pos, num_speed=10, method="linear"):
    return 0

#------------------------------------#
#        DEALING COORIDATORS         # 
#------------------------------------#

def coord_object_full(arr_in, arr_pos, arr_center=[0,0], num_tilt=0, num_angle=0, num_scale=1):
  # Postion of a object on the system, while turning and tilting
  # Center of rotation is (0,0) in arr_in, which is the center of the object
  num_points = len(arr_in)
  # First make an array of position
  arr_tmp = [[0 , 0] for n in range(num_points) ]
  arr_out = [[arr_pos[0], arr_pos[1]] for n in range(num_points) ]
  # position + Shape = final position
  for n in range(num_points):
    arr_tmp[n][0] += (arr_in[n][0]) * a_cos(num_tilt)  
    arr_tmp[n][1] += arr_in[n][1] #- arr_center[1]
    num_leng, num_theta = num_C2P(arr_tmp[n], arr_center)
    arr_out[n][0] += num_leng * a_sin(num_angle + num_theta) * num_scale
    arr_out[n][1] += num_leng * a_cos(num_angle + num_theta) * num_scale 
  return arr_out

def pos_os(arr_in, arr_camera_para):
  # Position of the object coordination on the screen
  # all the points must fit to the point on screen.
  num_points = len(arr_in)
  # First make an array of position
  arr_center = arr_camera_para["arr_center"]
  arr_screen_size   = arr_camera_para["arr_screen_size"]
  num_Yend          = arr_camera_para["num_Yend"] 
  num_Xend          = arr_camera_para["num_Xend"] 
  num_Xsta          = arr_camera_para["num_Xsta"] 
  arr_out = [ [0,0] for n in range(num_points) ]

  for n in range(num_points):
    num_leng, num_theta = num_C2P(arr_in[n], arr_center)
    num_theta_sum = arr_camera_para["Camera_angle"] - num_theta
    arr_out[n][0] = -num_leng * a_sin(num_theta_sum) + arr_camera_para["arr_center"][0] - num_Xsta
    arr_out[n][1] = num_Yend - (arr_center[1] + num_leng * a_cos(num_theta_sum))
  return arr_out

def posico(arr_pos, arr_screen_size):
  # POSITIVE COORDINATION
  return [ arr_pos[0] - arr_screen_size[0]  , arr_screen_size[1] - arr_pos[1]]
  
def cenpos(arr_pos, arr_center, num_scale, num_angle, arr_0center=[0,0]):
  # Check the CENtral POSition 
  arr_out = [arr_pos[0], arr_pos[1]]
  num_length, num_theta = num_C2P(arr_center, arr_0center)
  arr_out[0] += a_sin(num_theta + num_angle) * num_length * num_scale
  arr_out[1] += a_cos(num_theta + num_angle) * num_length * num_scale
  return arr_out

def shiftpos(arr_pos, arr_center):
  arr_out=[arr_pos[0], arr_pos[1]]
  arr_out[0] += arr_center[0]
  arr_out[1] += arr_center[1]
  return arr_out

#------------------------------------#
#              EFFECTS               # 
# There will be object of effect     #
#------------------------------------#

def shield_hit(arr_shield_center, num_shield_range, num_scale, arr_shield_color_sta, arr_shield_color_end,  num_left_time, num_dis_time, var_screen, num_rate=1, num_shield_thick=1):
  # The circle will dim with time. 
  arr_color = [0,0,0]
  num_color_ratio = float(num_left_time) / float(num_dis_time)
  for n in range(3):
    arr_color[n] = int(ratio(arr_shield_color_sta[n],arr_shield_color_end[n], num_color_ratio))
  pygame.draw.circle(var_screen, arr_color, arr_shield_center, int(num_shield_range*num_scale), num_shield_thick  )
  num_left_time -= num_rate
  if num_left_time <= 0:
    if_exist = False
  else:
    if_exist = True
  return num_left_time, if_exist

def body_hit(arr_pos, num_scale, num_left_time, var_screen, num_weapon_angle, num_weapon_velocity, num_spread_angle, num_spread_quantity=3, num_spread_basic=3, num_dmg_scale=1, num_rate=1):
  num_spread = num_spread_num_spread_basic + random.randrange(num_spread_quantity)
  arr_spread = [[0.0, 0.0, True] for n in range(num_spread)]
  # angle, speed
  arr_spread_random = random.sample(range(-10, 11), num_spread)
  for n in range(num_spread):
    arr_spread[0] = num_weapon_angle + num_spread_angle * (arr_spread_random[n] / 10.0)
    arr_spread[1] = num_weapon_velocity * abs(arr_spread_random[n] / 10.0)

  num_left_time -= num_rate    
  if num_left_time <= 0:
    if_exist = False
  else:
    if_exist = True
  return num_left_time, if_exist  


def engine_tail(arr_plasma_pos, str_plasma_color, ):
  
  return 0  


#------------------------------------#
#       Physical Reaction            #
#------------------------------------#

def collision_vel(arr_vel_o1, arr_pos_o1, num_mass_o1, num_angle_o1, arr_vel_o2, arr_pos_o2, num_mass_o2, num_angle_o2):
    """
    PS: the loss of velocity is wrong now. should be calculated as 
    V_loss = 2(m1v1 -m2v1)/(m1+m2)
    """
    num_vX_o1        = 0.0
    num_vY_o1        = 0.0
    num_vX_o2        = 0.0
    num_vY_o2        = 0.0

    num_total_mass    = num_mass_o1 + num_mass_o2
    num_mass_parti_o1 = num_mass_o2 / num_total_mass
    num_mass_parti_o2 = num_mass_o1 / num_total_mass

    num_angle_n1 = num_C2P(arr_pos_o2, arr_pos_o1)[1]
    num_angle_n2 = num_C2P(arr_pos_o1, arr_pos_o2)[1]
#print("num_angle_n1", num_angle_n1, "num_angle_n2", num_angle_n2)
    num_angle_diff_o1Y = math.fmod(num_angle_n1 - num_angle_o1[0] + 360    , 360 )
    num_angle_diff_o2Y = math.fmod(num_angle_n2 - num_angle_o2[0] + 360    , 360 ) 
    num_angle_diff_o1X = math.fmod(num_angle_o1[0] + 90 - num_angle_n1 + 360, 360) 
    num_angle_diff_o2X = math.fmod(num_angle_o2[0] + 90 - num_angle_n2 + 360, 360) 
#print("num_angle_diff_o1X", num_angle_diff_o1X, "num_angle_diff_o2X", num_angle_diff_o2X) 
    num_o1v1_loss = a_cos(num_angle_diff_o1Y) * (arr_vel_o1[1] )
    num_o1v0_loss = a_cos(num_angle_diff_o1X) * (arr_vel_o1[0] ) 
    
# Temp solution
    if arr_vel_o1 > 0:
        tmp_angle = 0
    else: 
        tmp_angle = 180
#if num_angle_diff_o1Y + tmp_angle  <= 90 or num_angle_diff_o1Y + tmp_angle >= 270:
#if num_angle_diff_o1Y <= 90 or num_angle_diff_o1Y >= 270:
    num_vY_o1 -=  num_o1v1_loss * a_cos(num_angle_diff_o1Y) * num_mass_parti_o1 
    num_vX_o1 -=  num_o1v1_loss * a_sin(num_angle_diff_o1Y) * num_mass_parti_o1
    num_vY_o2 -=  num_o1v1_loss * a_cos(num_angle_diff_o2Y) * num_mass_parti_o2 
    num_vX_o2 -=  num_o1v1_loss * a_sin(num_angle_diff_o2Y) * num_mass_parti_o2
    if num_angle_diff_o1X + num_angle_o1[1] <= 90  or num_angle_diff_o1X + num_angle_o1[1] >= 270:
        num_vY_o1 -=  num_o1v0_loss * a_sin(num_angle_diff_o1X) * num_mass_parti_o1 
        num_vX_o1 -=  num_o1v0_loss * a_cos(num_angle_diff_o1X) * num_mass_parti_o1 
        num_vY_o2 -=  num_o1v0_loss * a_sin(num_angle_diff_o2X) * num_mass_parti_o2 
        num_vX_o2 -=  num_o1v0_loss * a_cos(num_angle_diff_o2X) * num_mass_parti_o2 

    return [ num_vX_o1, num_vY_o1, num_vX_o2, num_vY_o2] 

def collision_vel_bk2(arr_vel_o1, arr_pos_o1, num_mass_o1, num_angle_o1, arr_vel_o2, arr_pos_o2, num_mass_o2, num_angle_o2):
    """
    PS: the loss of velocity is wrong now. should be calculated as 
    V_loss = 2(m1v1 -m2v1)/(m1+m2)
    only the direction of -x did not solve
    Backup if mess-up
    """
    num_vX_o1        = 0.0
    num_vY_o1        = 0.0
    num_vX_o2        = 0.0
    num_vY_o2        = 0.0

    num_total_mass    = num_mass_o1 + num_mass_o2
    num_mass_parti_o1 = num_mass_o2 / num_total_mass
    num_mass_parti_o2 = num_mass_o1 / num_total_mass

    num_angle_n = math.fmod(num_C2P(arr_pos_o2, arr_pos_o1)[1], 360) #- 180.0
    num_angle_diff_o1Y = num_angle_n - math.fmod(num_angle_o1[0], 360)
    num_angle_diff_o2Y = num_angle_n - math.fmod(num_angle_o2[0], 360) 
    num_angle_diff_o1X = num_angle_n - math.fmod(num_angle_o1[0]+90, 360) 
    num_angle_diff_o2X = num_angle_n - math.fmod(num_angle_o2[0]+90, 360) 

    num_o1v1_loss = a_cos(num_angle_diff_o1Y) * (arr_vel_o1[1] )
    num_o1v0_loss = a_cos(num_angle_diff_o1X) * (arr_vel_o1[0] ) 
    num_o2v1_loss = a_cos(num_angle_diff_o2Y) * (arr_vel_o2[1] )
    num_o2v0_loss = a_cos(num_angle_diff_o2X) * (arr_vel_o2[0] ) 

    num_vY_o1 -=  num_o1v1_loss * a_cos(num_angle_diff_o1Y) * num_mass_parti_o1 
    num_vX_o1 -=  num_o1v1_loss * a_sin(num_angle_diff_o1Y) * num_mass_parti_o1
    num_vY_o2 +=  num_o1v1_loss * a_cos(num_angle_diff_o2Y) * num_mass_parti_o2 
    num_vX_o2 +=  num_o1v1_loss * a_sin(num_angle_diff_o2Y) * num_mass_parti_o2

    num_vY_o1 +=  num_o2v1_loss * a_cos(num_angle_diff_o1Y) * num_mass_parti_o1 
    num_vX_o1 +=  num_o2v1_loss * a_sin(num_angle_diff_o1Y) * num_mass_parti_o1
    num_vY_o2 -=  num_o2v1_loss * a_cos(num_angle_diff_o2Y) * num_mass_parti_o2 
    num_vX_o2 -=  num_o2v1_loss * a_sin(num_angle_diff_o2Y) * num_mass_parti_o2

    num_vY_o1 -=  num_o1v0_loss * a_sin( num_angle_diff_o1X) * num_mass_parti_o1 
    num_vX_o1 -=  num_o1v0_loss * a_cos( num_angle_diff_o1X) * num_mass_parti_o1 
    num_vY_o2 +=  num_o1v0_loss * a_sin( num_angle_diff_o2X) * num_mass_parti_o2 
    num_vX_o2 +=  num_o1v0_loss * a_cos( num_angle_diff_o2X) * num_mass_parti_o2 

    num_vY_o1 +=  num_o2v0_loss * a_sin( num_angle_diff_o1X) * num_mass_parti_o1 
    num_vX_o1 +=  num_o2v0_loss * a_cos( num_angle_diff_o1X) * num_mass_parti_o1 
    num_vY_o2 -=  num_o2v0_loss * a_sin( num_angle_diff_o2X) * num_mass_parti_o2 
    num_vX_o2 -=  num_o2v0_loss * a_cos( num_angle_diff_o2X) * num_mass_parti_o2 

    return [ num_vX_o1, num_vY_o1, num_vX_o2, num_vY_o2] 

def collision_vel_BK2(arr_vel_o1, arr_pos_o1, num_mass_o1, num_angle_o1, arr_vel_o2, arr_pos_o2, num_mass_o2, num_angle_o2):
    """
    PS: the loss of velocity is wrong now. should be calculated as 
    V_loss = 2(m1v1 -m2v1)/(m1+m2)
    only the direction of -x did not solve
    Backup if mess-up
    """
    num_vX_o1        = 0.0
    num_vY_o1        = 0.0
    num_vX_o2        = 0.0
    num_vY_o2        = 0.0

    num_total_mass    = num_mass_o1 + num_mass_o2
    num_mass_parti_o1 = num_mass_o2 / num_total_mass
    num_mass_parti_o2 = num_mass_o1 / num_total_mass

    num_angle_n = math.fmod(num_C2P(arr_pos_o2, arr_pos_o1)[1], 360) #- 180.0
    num_angle_diff_o1Y = num_angle_n - math.fmod(num_angle_o1[0], 360)
    num_angle_diff_o2Y = num_angle_n - math.fmod(num_angle_o2[0], 360) 
# new 
#num_angle_diff_o1X = min( max( math.fmod(num_angle_o1[0]+90, 360) - num_angle_n , -90), 90)
#num_angle_diff_o2X = min( max( math.fmod(num_angle_o2[0]+90, 360) - num_angle_n , -90), 90)
# old
    num_angle_diff_o1X = math.fmod(num_angle_o1[0]+90, 360) - num_angle_n
    num_angle_diff_o2X = math.fmod(num_angle_o2[0]+90, 360) - num_angle_n 

#print("DIFF Y", num_angle_diff_o1Y, num_angle_diff_o2Y)
#print("DIFF X", num_angle_diff_o1X, num_angle_diff_o2X)
    num_o1v1_loss = a_cos(num_angle_diff_o1Y) * (arr_vel_o1[1] )
    num_o1v0_loss = a_cos(min(max(num_angle_diff_o1X, -90), 90)) * (arr_vel_o1[0] ) * a_cos(num_angle_o1[1])
    num_o2v1_loss = a_cos(num_angle_diff_o2Y) * (arr_vel_o2[1] )
    num_o2v0_loss = a_cos(min(max(num_angle_diff_o2X, -90), 90)) * (arr_vel_o2[0] ) * a_cos(num_angle_o2[1])

#print("NUM_o1v0_loss", num_o1v0_loss, "NUM_o2v0_loss", num_o2v0_loss)

    num_vY_o1 -=  num_o1v1_loss * a_cos(num_angle_diff_o1Y) * num_mass_parti_o1 
    num_vX_o1 -=  num_o1v1_loss * a_sin(num_angle_diff_o1Y) * num_mass_parti_o1
    num_vY_o2 +=  num_o1v1_loss * a_cos(num_angle_diff_o2Y) * num_mass_parti_o2 
    num_vX_o2 +=  num_o1v1_loss * a_sin(num_angle_diff_o2Y) * num_mass_parti_o2

    num_vY_o1 +=  num_o2v1_loss * a_cos(num_angle_diff_o1Y) * num_mass_parti_o1 
    num_vX_o1 +=  num_o2v1_loss * a_sin(num_angle_diff_o1Y) * num_mass_parti_o1
    num_vY_o2 -=  num_o2v1_loss * a_cos(num_angle_diff_o2Y) * num_mass_parti_o2 
    num_vX_o2 -=  num_o2v1_loss * a_sin(num_angle_diff_o2Y) * num_mass_parti_o2

    num_vY_o1 -=  num_o1v0_loss * a_sin( num_angle_diff_o1X) * num_mass_parti_o1 * a_cos(num_angle_o1[1])
    num_vX_o1 -=  num_o1v0_loss * a_cos( num_angle_diff_o1X) * num_mass_parti_o1 * a_cos(num_angle_o1[1])
    num_vY_o2 +=  num_o1v0_loss * a_sin( num_angle_diff_o2X) * num_mass_parti_o2 * a_cos(num_angle_o2[1])
    num_vX_o2 +=  num_o1v0_loss * a_cos( num_angle_diff_o2X) * num_mass_parti_o2 * a_cos(num_angle_o2[1])
    # old
#    num_vY_o1 +=  num_o2v0_loss * a_sin( num_angle_diff_o1X) * num_mass_parti_o1 * a_cos(num_angle_o2[1])
#    num_vX_o1 +=  num_o2v0_loss * a_cos( num_angle_diff_o1X) * num_mass_parti_o1 * a_cos(num_angle_o2[1])
#    num_vY_o2 -=  num_o2v0_loss * a_sin( num_angle_diff_o2X) * num_mass_parti_o2 * a_cos(num_angle_o2[1])
#    num_vX_o2 -=  num_o2v0_loss * a_cos( num_angle_diff_o2X) * num_mass_parti_o2 * a_cos(num_angle_o2[1])
    # new
#    num_vY_o1 +=  num_o2v0_loss * a_sin( num_angle_diff_o1X) * num_mass_parti_o1 
#    num_vX_o1 +=  num_o2v0_loss * a_cos( num_angle_diff_o1X) * num_mass_parti_o1 
#    num_vY_o2 -=  num_o2v0_loss * a_sin( num_angle_diff_o2X) * num_mass_parti_o2 
#    num_vX_o2 -=  num_o2v0_loss * a_cos( num_angle_diff_o2X) * num_mass_parti_o2 

    return [ num_vX_o1, num_vY_o1, num_vX_o2, num_vY_o2] 

def drag_force(num_v, num_rho=0.179, C_D=0.47, A = 1.0):
    # Drag force = F = 0.5 * rho * v**2 * C_D * A
    # C_D for sphere: 0.47; rho for helium = 0.179 kg/m ; assuming A = 1.0
    num_drag_force = -0.5 * num_v ** 2 * num_rho * 9.8 * C_D * A 
    return num_drag_force



#------------------------------------#
#       AIs                          #
#------------------------------------#

def AI_detect_object(arr_Objects, num_Objects, num_detect_radius, object_self):
    arr_detect_Obj = []
    for obj_i in range(num_Objects):
        num_dist, num_phi = num_C2P(object_self.arr_pos, arr_Objects[obj_i].arr_pos)	
	if num_dist < num_detect_radius and arr_Objects[obj_i].str_ID != object_self.str_ID:
            arr_detect_Obj.append([arr_Objects[obj_i].str_ID, num_dist, num_phi  ])
    return arr_detect_Obj

#def AI_avoid_crash(arr_detect_Obj, arr_detect_objs):
#    for arr_content in arr_detect_objs:
#if arr_content[num_dist]

    return 0 
def AI_moving(Obj_self, str_pattern, ):
    return 0

def AI_missile(arr_pos, arr_tg_pos, str_target_ID ):
  # calculating the distance
  

  # calculating the angle


  # returns the control/displacement?

  return 0  
#------------------------------------#
#       information display          #
#------------------------------------#



#------------------------------------#
#              GAME CONTROL          # 
#------------------------------------#



def sys_cd_time(num_game_time, str_tarvar, param_weapon):
  # The weapons require the cool-down time
  for n in range(len(param_weapon["name"])):
    if param_weapon["name"][n] == str_tarvar:
      num_n = n
  if param_weapon["num_cd_count"][num_n] + param_weapon["num_cd_time"][num_n]  < num_game_time :
    param_weapon["if_fire"][num_n] = True
  else: 
    param_weapon["if_fire"][num_n] = False

def check_hit(arr_obj1_center, arr_obj2_center, num_obj1_range, num_obj2_range, num_obj1_scale, num_obj2_scale):
  num_distance = ((arr_obj1_center[0] - arr_obj2_center[0])**2 + (arr_obj1_center[1] - arr_obj2_center[1])**2) ** 0.5
  #print arr_obj1_center,arr_obj2_center
  if num_distance <= num_obj1_range * num_obj1_scale + num_obj2_range * num_obj2_scale:
    return True 
  else:
    return False

def check_weapon_hit(obj_mot, obj_unc):
  # check how obj is affected by the weapon
  if obj_mot.SH > obj_unc.num_SH_dmg:
    obj_mot.SH -= obj_unc.num_SH_dmg 
  else: 
    obj_mot.HP -= obj_unc.num_HP_dmg 
    obj_mot.SH  = 0 
  obj_mot.EP   -= obj_unc.num_EP_dmg 
  if obj_mot.HP <=0:
    obj_mot.if_exist = False
  return obj_mot

def game_quit():
  pygame.quit()
  print("Game is terminated.")
  print("Bye Bye !")


#------------------------------------#
#              MAIN GAME             # 
#------------------------------------#


def main_game(screen_size, num_uni_scale=1.0, num_time_limit=0):

# ------------------------------------------------------- # 
# Gaming information setup: Camera                        #
# ------------------------------------------------------- # 
#  put in the camera

  pygame.font.init()
  screen_size = (screen_size[0], screen_size[1])
  screen = pygame.display.set_mode(screen_size)

  if_run     = True
  num_second = 0.0 
  
  num_time_scale  = 1.0  # for tick = 120, 1 sec is for 1.0 as scale

  camera = Camera(screen_size)

  # -------------------------------------------- #
  #               Object information             #
  # -------------------------------------------- #

  arr_mapsize  = [4000, 8000]
  num_gridsize = 200
  arr_num_grid = [arr_mapsize[0]/num_gridsize, arr_mapsize[1]/num_gridsize ]

  arr_player_init = [screen_size[0]*0.5, screen_size[1]*0.2] 

  player = MotionObject([screen_size[0]*0.5, screen_size[1]*0.2],0,300,200,200)
  player.num_scale  = 2 * num_uni_scale
  player.str_ID     = "PYR1"

  arr_body_e1       = [[-2,3],[-1,7],[0,10],[1,7],[2,3]]
  num_hit_range_e1  = 2.0
  arr_hit_center_e1 = [0,6.5]
  num_scale_e1      = 2 * num_uni_scale  
  num_angle_e1     = 180

  arr_body_e2       = [[0,12],[2,10],[3,9],[3,4],[2,3],[1,2],[0,0],[-1,2],[-2,3],[-3,4],[-3,9],[-2,10]]
  num_hit_range_e2  = 3  
  arr_hit_center_e2 = [0 ,6  ]
  num_scale_e2      = 2 * num_uni_scale

  print("load emeny")
  E3_demo = MotionObject([200,200], 360 * random.random(), str_ID="E3_20")
  E3_demo.arr_body       = arr_body_e2
  E3_demo.arr_color      = (255,255,0)
  E3_demo.num_scale      = num_uni_scale * 2.0
  E3_demo.num_hit_range  = num_hit_range_e2
  E3_demo.arr_hit_center = arr_hit_center_e2

  test_msl = MotionObject(5,10, [200,200])
  test_msl.arr_body = [[0,15],[1,13],[1,11],[2,10],[1,10],[1,4],[2,3],[2,2],[1,2],[1,0],[-1,0],[-1,2],[-2,2],[-2,3],[-1,4],[-1,10],[-2,10],[-1,11],[-1,13]] 
  test_msl.num_scale = 2 

  arr_laser_shape = [[0,3 ],[0, 0]]
  arr_ion_shape = [[0,3 ],[0, 0]]

#  coodination system
  arr_coord_XY = list([[[] for l in range(arr_num_grid[0])] for k in range(arr_num_grid[1])])
  for j in range(arr_num_grid[1]):
    for i in range(arr_num_grid[0]):
      arr_coord_XY[j][i] = [i*num_gridsize, j*num_gridsize] 

#   On screen objs
  arr_MotionObjects    = []
  arr_UncontrolObjects = []
  arr_EffectObjects    = []
 
  arr_ss1 = screen_size
  arr_ss0 = screen_size

# Put player as the first object:
  #arr_MotionObjects.append(player)

  # -------------------------------------------- #
  #               Sound  information             #
  # -------------------------------------------- #
  pygame.mixer.init()
  obj_s_blast = pygame.mixer.Sound("./aaj_0020_Lazer_Gun_01_SFX.ogg")
  obj_s_explo = pygame.mixer.Sound("./audio_hero_ExplosionAtomic_DIGIVJ1_91_349_2.ogg")
  pygame.joystick.quit()
  pygame.joystick.init()
  #print(pygame.joystick.Joystick)
#pygame.joystick.Joystick(0).init()

  while if_run:
#   Pygame setup
    clock = pygame.time.Clock()
    event = pygame.event.get()
    focused = pygame.key.get_focused()
    time_tick = pygame.time.get_ticks()

    for event in pygame.event.get(): # User did something.
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
	else:
	    print(event, event.type)

#    print("Joysticks: {0:d}".format(pygame.joystick.get_count()))
#print(pygame.joystick.Joystick(1).get_button())
#   On screen setup
    pause = 100
    screen.fill((0,0,0))
    font = pygame.font.SysFont("monospace",18)

#   On screen information
    label1 = font.render("time: {0:1.1f}".format(num_second),True,(225,225,225))
    screen.blit(label1,  [ 5,40])
    label2 = font.render("X:{0:5.1f}, Y:{1:5.1f}, R:{2:5.2f}".format(player.arr_pos[0], player.arr_pos[1], player.num_angle[0]), True, (225,225,225))    
    screen.blit(label2,  [ 5,60])
    label3 = font.render("HP: {2:.0f}/{0:.0f} EP: {3:.0f}/{1:.0f}".format(player.MAX_HP, player.MAX_EP, player.HP, player.EP), True, (255,255,255))
    screen.blit(label3,  [ 5,80])
    
#   Control
    if focused:
      pressed = pygame.key.get_pressed()
      
    if pressed[pygame.K_UP  ] :
#      player.POS_Y  +=  -5.0
      player.power_system(True, False, True )
    if pressed[pygame.K_DOWN] :
#      player.POS_Y  +=  +5.0
      player.power_system(False, True, True )
    if pressed[pygame.K_UP] == False and pressed[pygame.K_DOWN]== False :
      player.power_system(False, False, False)

    if pressed[pygame.K_RIGHT]:
      player.tilt_system(True ,False, True)
    if pressed[pygame.K_LEFT] :
      player.tilt_system(False,True , True)
    if pressed[pygame.K_LEFT] == False and pressed[pygame.K_RIGHT]== False :
      player.tilt_system(False, False, False)
    else:
      player.if_tilt = True 
    if pressed[pygame.K_e]:
      player.turn_system(True , False)
    if pressed[pygame.K_q]:
      player.turn_system(False, True )
    if pressed[pygame.K_e] == False and pressed[pygame.K_q] == False:
      player.turn_system(False, False)

#   Mouse Information
    arr_MPos   = pygame.mouse.get_pos()
    arr_MPress = pygame.mouse.get_pressed()
    if arr_MPress[0] == 1:
        print(arr_MPress, arr_MPos)

    player.self_physics()
    # Control: firing system
    # Firing weapon
    if pressed[pygame.K_v]:
      player.fire_weapon(num_game_time=time_tick, if_fire=True)
      if player.param_weapon["if_fire"][0]:
        obj_s_blast.play()
        for n in range(len(player.arr_gun_point)):
          arr_UncontrolObjects.append(UncontrolObject(player.arr_fire_point[n], player.num_angle[0], player.param_weapon["speed"][0], player.param_weapon["lasttime"][0], player.param_weapon["arr_color"][0], player.param_weapon["arr_shape"][0] , arr_dmg=[player.param_weapon["num_HP_damage"][0], player.param_weapon["num_SH_damage"][0],player.param_weapon["num_EP_damage"][0]]))
    else:
      player.fire_weapon(if_fire=False)
    # Firing Canon
    if pressed[pygame.K_c]:
      player.fire_weapon(num_game_time=time_tick, if_fire=True)
      if player.param_weapon["if_fire"][1]:
        obj_s_blast.play()
        for n in range(len(player.arr_gun_point)):
          arr_UncontrolObjects.append(UncontrolObject(player.arr_fire_point[n], player.num_angle[0], player.param_weapon["speed"][1], player.param_weapon["lasttime"][1], player.param_weapon["arr_color"][1], player.param_weapon["arr_shape"][1] , arr_dmg=[player.param_weapon["num_HP_damage"][1], player.param_weapon["num_SH_damage"][1],player.param_weapon["num_EP_damage"][1]]))
    else:
      player.fire_weapon(if_fire=False)

    # Firing Missile
    if pressed[pygame.K_x]:
      player.fire_weapon(num_game_time=time_tick, if_fire=True)
      if player.param_weapon["if_fire"][2]:
        num_gunpoint = 0
        arr_UncontrolObjects.append(UncontrolObject(player.arr_fire_point[num_gunpoint], player.num_angle[0], player.param_weapon["speed"][2], player.param_weapon["lasttime"][2], player.param_weapon["arr_color"][2], player.param_weapon["arr_shape"][2] , arr_dmg=[player.param_weapon["num_HP_damage"][2], player.param_weapon["num_SH_damage"][2],player.param_weapon["num_EP_damage"][2]]))

    if pressed[pygame.K_z]:
      player.locking_system()
    # Cooling down
    sys_cd_time(time_tick, "laser" , player.param_weapon)
    sys_cd_time(time_tick, "ion"   , player.param_weapon)
    sys_cd_time(time_tick, "aa-msl", player.param_weapon)

    if pressed[pygame.K_r]:
      player.add_missile([10,10],"anti-fighter")

    # Setting for camera (following object): 
    arr_camera_para = camera.follow_object(arr_player_init, player.arr_pos, player.num_angle[0])

    # Control: moving player back to original point

    if pressed[pygame.K_o]:
      player.arr_pos[0] = arr_player_init[0]
      player.arr_pos[1] = arr_player_init[1]

    if pressed[pygame.K_ESCAPE] :
      game_quit()
      break

# ------------------------------------- #
#              Load Enemies             #
# ------------------------------------- #

    for time_t in range(0,1000, 50 ):
      if time_tick/10 == time_t:
        RAN_X = random.randint(10,arr_ss1[0]) 
        RAN_Y = random.randint(10,arr_ss1[1]) 
        # arr format : [position_x, position_y], deg. of rotation, num_Enemy_HP, arr of body, ID, enemy_hit_center, hit range
        arr_MotionObjects.append(MotionObject([RAN_X, RAN_Y], num_angle_e1, str_ID="E1_{0:d}".format(time_tick), num_hp=100, num_ep=200, num_sh=200))
        arr_MotionObjects[-1].arr_body =  arr_body_e1 
        arr_MotionObjects[-1].num_hit_range  = num_hit_range_e1
        arr_MotionObjects[-1].arr_hit_center = arr_hit_center_e1
        arr_MotionObjects[-1].num_scale      = num_scale_e1


        #print(arr_enemy[-1][6])

    for time_t in range(0,20000,200):
      if time_tick/10 == time_t:
        RAN_X = random.randint(10,arr_ss1[0]) 
        RAN_Y = random.randint(10,arr_ss1[1]) 

        arr_MotionObjects.append(MotionObject([RAN_X, RAN_Y], 360 * random.random(), str_ID="E2_{0:d}".format(time_tick)))
        arr_MotionObjects[-1].arr_body =  arr_body_e2 
        arr_MotionObjects[-1].num_hit_range  = num_hit_range_e2
        arr_MotionObjects[-1].arr_hit_center = arr_hit_center_e2
        arr_MotionObjects[-1].num_scale      = num_scale_e2


    E3_demo.arr_velocity[1] = 1.0
    E3_demo.num_angle[0] += 2.0
    E3_demo.self_physics()


    
# ---------------------------------- #
# Draw all the things                #
# ---------------------------------- #

    arr_smlrtc = [[1,-1],[1,1],[-1,1],[-1,-1]]

#   Draw Player:
    pygame.draw.lines(screen, player.arr_color, True, pos_os(coord_object_full  (player.arr_body , player.arr_pos, num_tilt=player.num_tilt, num_angle=player.num_angle[0], num_scale= player.num_scale, arr_center=player.arr_hit_center),arr_camera_para ))

#   Draw Enemy E3:
    pygame.draw.lines(screen, E3_demo.arr_color, True, pos_os(coord_object_full  (E3_demo.arr_body , E3_demo.arr_pos, num_tilt=E3_demo.num_tilt, num_angle=E3_demo.num_angle[0], num_scale= E3_demo.num_scale, arr_center=E3_demo.arr_hit_center),arr_camera_para ))


    # --------------------------------------- #
    #   Check MotionObjects                   #
    # --------------------------------------- #
    num_detect=0 
    num_MotObj = len(arr_MotionObjects)
    num_UncObj = len(arr_UncontrolObjects)
    num_EffObj = len(arr_EffectObjects)
    for num_mo in range(num_MotObj):
#   Draw things in arr_MotionObjects
        arr_MotionObjects[num_mo].self_physics()
        #arr_MotionObjects[num_mo].power_system(True , False, True )
        pygame.draw.lines(screen, arr_MotionObjects[num_mo].arr_color, True, pos_os(coord_object_full  (arr_MotionObjects[num_mo].arr_body , arr_MotionObjects[num_mo].arr_pos, num_tilt=arr_MotionObjects[num_mo].num_tilt, num_angle=arr_MotionObjects[num_mo].num_angle[0], num_scale= arr_MotionObjects[num_mo].num_scale, arr_center=arr_MotionObjects[num_mo].arr_hit_center), arr_camera_para ))  
        # --------------------------------------- #
        #   Detect Objects                        #
        # --------------------------------------- #
        arr_detect_MotObj =  AI_detect_object(arr_MotionObjects, num_MotObj, arr_MotionObjects[num_mo].param_ai["Detect_Radius"], arr_MotionObjects[num_mo])
        if len(arr_detect_MotObj) >0:
	    num_detect += 1
	    num_ran1 = random.random()
	    num_ran2 = random.random()
	    num_ran3 = random.random()
            if num_ran1 > 0.5:
                arr_MotionObjects[num_mo].fire_weapon(if_fire=True)
                arr_MotionObjects[num_mo].tilt_system(False,  True, True )
            else:
                arr_MotionObjects[num_mo].tilt_system(True , False, True )
            if num_ran2 > 0.5:
                arr_MotionObjects[num_mo].power_system(False,  True, True )
            else:
                arr_MotionObjects[num_mo].power_system(True , False, True )
            if num_ran3 > 0.5:
                arr_MotionObjects[num_mo].turn_system(True, False)
            else:
                arr_MotionObjects[num_mo].turn_system(False, True)
            if num_ran3 > 0.9:
                arr_MotionObjects[num_mo].fire_weapon(num_game_time=time_tick, if_fire=True)
                if arr_MotionObjects[num_mo].param_weapon["if_fire"][0]:
                #obj_s_blast.play()
                    for n in range(len(arr_MotionObjects[num_mo].arr_gun_point)):
                        arr_UncontrolObjects.append(UncontrolObject(arr_MotionObjects[num_mo].arr_fire_point[n], arr_MotionObjects[num_mo].num_angle[0]     , arr_MotionObjects[num_mo].param_weapon["speed"][0], arr_MotionObjects[num_mo].param_weapon["lasttime"][0], arr_MotionObjects[num_mo].param_weapon["arr_color"][0], arr_MotionObjects[num_mo].param_weapon["arr_shape"][0] , arr_dmg=[arr_MotionObjects[num_mo].param_weapon["num_HP_damage"][0], arr_MotionObjects[num_mo].param_weapon["num_SH_damage"][0],arr_MotionObjects[num_mo].param_weapon["num_EP_damage"][0]]))
                else:
                    arr_MotionObjects[num_mo].fire_weapon(num_game_time=time_tick, if_fire=False)

 	    
        else:
            arr_MotionObjects[num_mo].tilt_system(False, False, False)
            arr_MotionObjects[num_mo].power_system(False, False, False)
            arr_MotionObjects[num_mo].turn_system(False, False)

        # --------------------------------------- #
        #   Check crash with player:              #
        # --------------------------------------- #
        if_hit = check_hit(shiftpos(arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].arr_hit_center), shiftpos(player.arr_pos, player.arr_hit_center), arr_MotionObjects[num_mo].num_hit_range, player.num_hit_range, arr_MotionObjects[num_mo].num_scale, player.num_scale  )

        if if_hit:
            [num_add_vel_o1_x1, num_add_vel_o1_y1 ,\
             num_add_vel_o2_x1, num_add_vel_o2_y1] = collision_vel(player.arr_velocity, player.arr_pos, player.num_mass, player.num_angle, arr_MotionObjects[num_mo].arr_velocity, arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].num_mass, arr_MotionObjects[num_mo].num_angle)
            [num_add_vel_o2_x2, num_add_vel_o2_y2 ,\
             num_add_vel_o1_x2, num_add_vel_o1_y2] = collision_vel( arr_MotionObjects[num_mo].arr_velocity, arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].num_mass, arr_MotionObjects[num_mo].num_angle, player.arr_velocity, player.arr_pos, player.num_mass, player.num_angle)
            player.arr_velocity[0] += num_add_vel_o1_x1 + num_add_vel_o1_x2
            player.arr_velocity[1] += num_add_vel_o1_y1 + num_add_vel_o1_y2
            arr_MotionObjects[num_mo].arr_velocity[0] += num_add_vel_o2_x1 + num_add_vel_o2_x2
            arr_MotionObjects[num_mo].arr_velocity[1] += num_add_vel_o2_y1 + num_add_vel_o2_y2

        # --------------------------------------- #
        #   Check crash with other Objects:       #
        # --------------------------------------- #

        for num_mo2 in range(num_MotObj):
            if num_mo != num_mo2:
                if_hit_oo = check_hit(shiftpos(arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].arr_hit_center), shiftpos(arr_MotionObjects[num_mo2].arr_pos, arr_MotionObjects[num_mo2].arr_hit_center), arr_MotionObjects[num_mo].num_hit_range, arr_MotionObjects[num_mo2].num_hit_range, arr_MotionObjects[num_mo].num_scale, arr_MotionObjects[num_mo2].num_scale  )
                if if_hit_oo:
                    [num_add_vel_o1_x1, num_add_vel_o1_y1 ,\
                     num_add_vel_o2_x1, num_add_vel_o2_y1] = collision_vel(arr_MotionObjects[num_mo].arr_velocity, arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].num_mass, arr_MotionObjects[num_mo].num_angle, arr_MotionObjects[num_mo2].arr_velocity, arr_MotionObjects[num_mo2].arr_pos, arr_MotionObjects[num_mo2].num_mass, arr_MotionObjects[num_mo2].num_angle)
                    [num_add_vel_o2_x2, num_add_vel_o2_y2 ,\
                     num_add_vel_o1_x2, num_add_vel_o1_y2] = collision_vel(arr_MotionObjects[num_mo2].arr_velocity, arr_MotionObjects[num_mo2].arr_pos, arr_MotionObjects[num_mo2].num_mass, arr_MotionObjects[num_mo2].num_angle, arr_MotionObjects[num_mo].arr_velocity, arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].num_mass, arr_MotionObjects[num_mo].num_angle)
                    arr_MotionObjects[num_mo].arr_velocity[0] += num_add_vel_o1_x1 + num_add_vel_o1_x2
                    arr_MotionObjects[num_mo].arr_velocity[1] += num_add_vel_o1_y1 + num_add_vel_o1_y2
                    arr_MotionObjects[num_mo2].arr_velocity[0] += num_add_vel_o2_x1 + num_add_vel_o2_x2
                    arr_MotionObjects[num_mo2].arr_velocity[1] += num_add_vel_o2_y1 + num_add_vel_o2_y2
#   Draw UncontrolObjects:
    for num_uo in range(num_UncObj):
      arr_UncontrolObjects[num_uo].cal_time()
      arr_UncontrolObjects[num_uo].cal_position()
      pygame.draw.lines(screen, arr_UncontrolObjects[num_uo].arr_color, True, pos_os(coord_object_full  (arr_UncontrolObjects[num_uo].arr_shape, arr_UncontrolObjects[num_uo].arr_pos, num_angle=arr_UncontrolObjects[num_uo].num_angle, num_scale= player.num_scale, arr_center=[0,0]), arr_camera_para)) 
# --------------------------------------- #
#           Object Check hit              #
# --------------------------------------- #

      for num_mo in range(num_MotObj):
        if_hit = check_hit(shiftpos(arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].arr_hit_center), arr_UncontrolObjects[num_uo].arr_pos, arr_MotionObjects[num_mo].num_hit_range, 1.0, arr_MotionObjects[num_mo].num_scale, player.num_scale  )

        if if_hit:
          # Object update information
          arr_MotionObjects[num_mo] = check_weapon_hit(arr_MotionObjects[num_mo],arr_UncontrolObjects[num_uo])    
#          print(num_mo, arr_MotionObjects[num_mo].HP, arr_MotionObjects[num_mo].SH, arr_MotionObjects[num_mo].EP)
          arr_UncontrolObjects[num_uo].if_exist = False
          # Adding effects
          
          arr_EffectObjects.append([arr_MotionObjects[num_mo].arr_pos, arr_MotionObjects[num_mo].arr_shield_center, arr_MotionObjects[num_mo].num_shield_range, 30, 30, True])

#   Draw Effect
    for num_eo in range(num_EffObj):
      arr_pos_eo = pos_os( coord_object_full([[0,0]], arr_EffectObjects[num_eo][0]), arr_camera_para) 
      num_left_time, if_exist = shield_hit([int(arr_pos_eo[0][0]), int(arr_pos_eo[0][1])  ], arr_EffectObjects[num_eo][2], player.num_scale, (  0,  0,  0), (255,255,255), arr_EffectObjects[num_eo][3], arr_EffectObjects[num_eo][4], screen) 
      arr_EffectObjects[num_eo][3] = num_left_time
      arr_EffectObjects[num_eo][5] = if_exist
    
    print(num_EffObj, num_MotObj, num_UncObj)

#print("number of detecting objects: {0:d}".format(num_detect))
          
# --------------------------------------- #
#           Checking Arrays               #
# --------------------------------------- #

    # Pop out if object is not existing anymore (if_exist = False)
    for num_mo in range(num_MotObj-1, -1, -1):
      if arr_MotionObjects[num_mo].if_exist == False:
        obj_s_explo.play()
        arr_MotionObjects.pop(num_mo)

    for num_uo in range(num_UncObj-1, -1, -1):
      if arr_UncontrolObjects[num_uo].if_exist == False:
        arr_UncontrolObjects.pop(num_uo)

    for num_eo in range(num_EffObj-1, -1, -1):
      if arr_EffectObjects[num_eo][5] == False:
        arr_EffectObjects.pop(num_eo)

    #   Processing game information
    num_second  = num_time_scale * time_tick / 1000   # to 0.1 second
    clock.tick(120/ num_time_scale)
    pygame.display.flip()

    if num_time_limit != 0:
        if num_time_scale * time_tick / 1000 >= num_time_limit:
            game_quit()


if __name__ == "__main__":
  #main_game([ 500 , 400])
  main_game([ 1500 , 800], num_uni_scale=2.0)
  #main_game([  800 , 640], num_uni_scale=0.9)

  #cProfile.run(main_game([1900,900] ))
