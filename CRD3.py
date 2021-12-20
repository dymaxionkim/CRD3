import os
import PySimpleGUI as sg
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
def Parameters():
    spec.loc['m']=[float(values['-m-']),'Module']
    spec.loc['zr']=[int(values['-zr-']),'Number of Teeth Ring']
    spec.loc['ze']=[int(values['-ze-']),'Diff of Teeth']
    spec.loc['h']=[float(values['-h-']),'Teeth Height Factor (0~1)']
    spec.loc['point']=[int(values['-point-']),'Control Points for One Tooth']
    spec.loc['X0']=[float(values['-X0-']),'Center Position']
    spec.loc['Y0']=[float(values['-Y0-']),'Center Position']
    spec.loc['WorkingDirectory']=[values['-WorkingDirectoty-'],'Working Directory']
    spec.loc['zd']=[spec.Content['zr']-spec.Content['ze'],'Number of Teeth Disc']
    spec.loc['Rbr']=[spec.Content['m']*spec.Content['zr'],'Radius of Base Circle for Ring']
    spec.loc['Rbd']=[spec.Content['m']*spec.Content['zd'],'Radius of Base Circle for Disc']
    spec.loc['Rar']=[spec.Content['Rbr']/spec.Content['zr'],'Radius of Rolling Circle for Ring']
    spec.loc['Rad']=[spec.Content['Rbd']/spec.Content['zd'],'Radius of Rolling Circle for Disc']
    spec.loc['thetaR']=[2*np.pi/spec.Content['zr'],'Pitch Angle of Ring [rad]']
    spec.loc['thetaD']=[2*np.pi/spec.Content['zd'],'Pitch Angle of Disc [rad]']
    spec.loc['qr']=[(np.pi*spec.Content['Rbr']/spec.Content['zr'])/2,'Radius of Roller for Ring']
    spec.loc['qd']=[(np.pi*spec.Content['Rbr']/spec.Content['zr'])/2,'Radius of Roller for Disc (equidistant distance)']
    spec.loc['er']=[spec.Content['Rar']*spec.Content['h'],'Eccentricity for Ring']
    spec.loc['ed']=[spec.Content['Rad']*spec.Content['h'],'Eccentricity for Disc']
    spec.loc['ea']=[spec.Content['Rbr']-spec.Content['Rbd'],'Actual Eccentricity for Disc']

def CRD3_PLOT(Xring,Yring,Xdisc,Ydisc):
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


##############################
# GUI
sg.theme('Default')
col = [[sg.Text('Working Directory :',size=(15,1)), sg.Input('./Result/',key='-WorkingDirectoty-',size=(16,1)), sg.FolderBrowse()],
        [sg.Text('Module, m =',size = (32,1)),sg.Input(1.0,key='-m-',size = (10,1)),sg.Text('[mm], (>0)')],
       [sg.Text('Number of Teeth Ring, zr =',size = (32,1)),sg.Input(40,key='-zr-',size = (10,1)),sg.Text('[ea], (Even Number)')],
       [sg.Text('Diff. of Ring and Disc, ze =',size = (32,1)),sg.Input(1,key='-ze-',size = (10,1)),sg.Text('[ea]')],
       [sg.Text('Teeth Height Factor, h =',size = (32,1)),sg.Input(0.7,key='-h-',size = (10,1)),sg.Text('(0~1)')],
       [sg.Text('Control Points for One Tooth, point =',size = (32,1)),sg.Input(50,key='-point-',size = (10,1)),sg.Text('[ea]')],
       [sg.Text('Center Position, X0 =',size = (32,1)),sg.Input(0.0,key='-X0-',size = (10,1)),sg.Text('[mm]')],
       [sg.Text('Center Position, Y0 =',size = (32,1)),sg.Input(0.0,key='-Y0-',size = (10,1)),sg.Text('[mm]')],
       [sg.Text('Bearing Size Factor =',size = (32,1)),sg.Input(0.6,key='-BEARING_FACTOR-',size = (10,1)),sg.Text('(0~1)')],
       [sg.Text('Pin Hole Size Factor =',size = (32,1)),sg.Input(0.6,key='-PIN_HOLE_FACTOR-',size = (10,1)),sg.Text('(0~1)')],
       [sg.Button('Run'), sg.Button('Exit')]]

layout = [[col]]
window = sg.Window('CRD3',layout,icon="CRD3.ico")

while True:
    event, values = window.read()
    spec = pd.DataFrame(columns=['Parameter','Content','Remark'])
    spec = spec.set_index('Parameter')

    try:
        Parameters()
    except:
        sg.popup('Type error.')

    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Run':
        os.makedirs(spec.Content['WorkingDirectory'],exist_ok=True)
        # Hypocycloid-like Tooth of Ring
        Xring,Yring,alphaR,betaR,phiR = HypoTooth(spec.Content['thetaR'],spec.Content['point'],spec.Content['Rar'],spec.Content['Rbr'],spec.Content['er'],spec.Content['qr'])
        # Hypocycloid-like Tooth of Disc
        Xdisc,Ydisc,alphaD,betaD,phiD = HypoTooth(spec.Content['thetaD'],spec.Content['point'],spec.Content['Rad'],spec.Content['Rbd'],spec.Content['ed'],spec.Content['qd'])
        CRD3_PLOT(Xring,Yring,Xdisc,Ydisc)
window.close()
