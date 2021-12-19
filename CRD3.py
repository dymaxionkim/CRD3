import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def Transform(Xinput,Yinput,Xmove,Ymove):
    Xoutput = Xinput + Xmove
    Youtput = Yinput + Ymove
    return Xoutput,Youtput

def TransRotation(Xcenter,Ycenter,Xinput,Yinput,Angle):
    Xinput2,Yinput2 = Transform(Xinput,Yinput,-Xcenter,-Ycenter)
    Xinput3 = np.cos(Angle)*Xinput2 - np.sin(Angle)*Yinput2
    Yinput3 = np.sin(Angle)*Xinput2 + np.cos(Angle)*Yinput2
    Xoutput,Youtput = Transform(Xinput3,Yinput3,Xcenter,Ycenter)
    return Xoutput,Youtput

# One Tooth Data
def HypoTooth(theta,point,Ra,Rb,e,q):
    # alpha : the angular position of the starting contact point and the current contact point of the base and the rolling circle in relation to the centre of the base circle
    alpha = np.linspace(0.0,theta,int(point))
    # beta : the swivel angle of the rolling circle
    beta = (Rb/Ra)*alpha
    # phi : The Auxiliary Angle
    phi = np.arctan(np.sin(beta)/((Ra/e)+np.cos(beta)))
    # Xh,Yh : One Hypocycloid-like Tooth
    Xh = (Rb+Ra)*np.cos(alpha)+e*np.cos(alpha+beta)-q*np.cos(alpha+np.arctan(phi))
    Yh = (Rb+Ra)*np.sin(alpha)+e*np.sin(alpha+beta)-q*np.sin(alpha+np.arctan(phi))
    return Xh,Yh,alpha,beta,phi

# Read Input Parameters
spec = pd.read_csv('./CRD3.csv',index_col='Parameter')
spec.loc['zd']=[spec.Content['zr']-spec.Content['ze'],'Number of Teeth Disc']
spec.loc['Rbr']=[spec.Content['m']*spec.Content['zr'],'Radius of Base Circle for Ring']
#spec.loc['Rbd']=[(spec.Content['zd']/(2*np.pi))*(2*np.pi*spec.Content['Rbr']/spec.Content['zr']),'Radius of Base Circle for Disc']
spec.loc['Rbd']=[spec.Content['m']*spec.Content['zd'],'Radius of Base Circle for Disc']
spec.loc['Rar']=[spec.Content['Rbr']/spec.Content['zr'],'Radius of Rolling Circle for Ring']
#spec.loc['Rad']=[spec.Content['Rar'],'Radius of Rolling Circle for Disc']
spec.loc['Rad']=[spec.Content['Rbd']/spec.Content['zd'],'Radius of Rolling Circle for Disc']
spec.loc['thetaR']=[2*np.pi/spec.Content['zr'],'Pitch Angle of Ring [rad]']
spec.loc['thetaD']=[2*np.pi/spec.Content['zd'],'Pitch Angle of Disc [rad]']
spec.loc['qr']=[(np.pi*spec.Content['Rbr']/spec.Content['zr'])/2,'Radius of Roller for Ring']
#spec.loc['qd']=[spec.Content['qr'],'Radius of Roller for Disc']
spec.loc['qd']=[(np.pi*spec.Content['Rbr']/spec.Content['zr'])/2,'Radius of Roller for Disc (equidistant distance)']
spec.loc['er']=[spec.Content['Rar']*spec.Content['h'],'Eccentricity for Ring']
#spec.loc['ed']=[spec.Content['er'],'Eccentricity for Disc']
spec.loc['ed']=[spec.Content['Rad']*spec.Content['h'],'Eccentricity for Disc']
spec.loc['ea']=[spec.Content['Rbr']-spec.Content['Rbd'],'Actual Eccentricity for Disc']

# Hypocycloid-like Tooth of Ring
Xring,Yring,alphaR,betaR,phiR = HypoTooth(spec.Content['thetaR'],spec.Content['point'],spec.Content['Rar'],spec.Content['Rbr'],spec.Content['er'],spec.Content['qr'])
# Hypocycloid-like Tooth of Disc
Xdisc,Ydisc,alphaD,betaD,phiD = HypoTooth(spec.Content['thetaD'],spec.Content['point'],spec.Content['Rad'],spec.Content['Rbd'],spec.Content['ed'],spec.Content['qd'])

# Figure
fig = plt.figure(figsize=(8,8))
plt.axes().set_aspect('equal')
plt.title('Cycloidal Eccentric Reducer Designer 3')
plt.grid(True)
# Plot Ring
circle = np.linspace(0.0,2*np.pi,360)
plt.plot(spec.Content['Rbr']*np.cos(circle),spec.Content['Rbr']*np.sin(circle),':',linewidth=1,color='grey')
for i in range(0,int(spec.Content['zr'])):
    Xring1,Yring1 = TransRotation(spec.Content['X0'],spec.Content['Y0'],Xring,Yring,i*spec.Content['thetaR'])
    plt.plot(Xring1,Yring1,'-',linewidth=1.5,color='black')
# Plot Disc
plt.plot(spec.Content['Rbd']*np.cos(circle)+spec.Content['ea'],spec.Content['Rbd']*np.sin(circle),':',linewidth=1,color='grey')
for i in range(0,int(spec.Content['zd'])):
    Xdisc1,Ydisc1 = TransRotation(spec.Content['X0'],spec.Content['Y0'],Xdisc,Ydisc,i*spec.Content['thetaD'])
    Xdisc2,Ydisc2 = Transform(Xdisc1,Ydisc1,spec.Content['ea'],0)
    plt.plot(Xdisc2,Ydisc2,'-',linewidth=1.5,color='blue')
plt.show()
