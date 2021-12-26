import os
import PySimpleGUI as sg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ezdxf

def Transform(Xinput,Yinput,Xmove,Ymove):
    Xoutput = Xinput + Xmove
    Youtput = Yinput + Ymove
    return Xoutput,Youtput

def Rotation(Xtemp,Ytemp,ANGLE,i):
    XX = np.cos(ANGLE*i)*Xtemp - np.sin(ANGLE*i)*Ytemp
    YY = np.sin(ANGLE*i)*Xtemp + np.cos(ANGLE*i)*Ytemp
    return XX,YY

def TransRotation(Xcenter,Ycenter,Xinput,Yinput,Angle):
    Xinput2,Yinput2 = Transform(Xinput,Yinput,-Xcenter,-Ycenter)
    Xinput3 = np.cos(Angle)*Xinput2 - np.sin(Angle)*Yinput2
    Yinput3 = np.sin(Angle)*Xinput2 + np.cos(Angle)*Yinput2
    Xoutput,Youtput = Transform(Xinput3,Yinput3,Xcenter,Ycenter)
    return Xoutput,Youtput

def Circle(DIA,SEG_CIRCLE):
    THETA0 = np.linspace(0.0,2*np.pi,SEG_CIRCLE)
    XX = DIA/2*np.sin(THETA0)
    YY = DIA/2*np.cos(THETA0)
    return XX,YY

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
def Parameters(STATE):
    spec.loc['WorkingDirectory']=[values['-WorkingDirectoty-'],'','Working Directory']
    spec.loc['zr']=[int(values['-zr-']),'ea','Number of Teeth Ring']
    spec.loc['ze']=[int(values['-ze-']),'ea','Diff of Teeth']
    spec.loc['h']=[float(values['-h-']),'','Teeth Height Factor (0~1)']
    spec.loc['point']=[int(values['-point-']),'ea','Control Points for One Tooth']
    spec.loc['X0']=[float(values['-X0-']),'mm','Center Position']
    spec.loc['Y0']=[float(values['-Y0-']),'mm','Center Position']
    spec.loc['zd']=[spec.Content['zr']-spec.Content['ze'],'ea','Number of Teeth Disc']
    spec.loc['thetaR']=[2*np.pi/spec.Content['zr'],'rad','Pitch Angle of Ring']
    spec.loc['thetaD']=[2*np.pi/spec.Content['zd'],'rad','Pitch Angle of Disc']
    spec.loc['seg_circle']=[360,'ea','Segmentation Points of Circle']
    spec.loc['pins']=[int(values['-pins-']),'ea','Number of Pins']
    spec.loc['angle_pins']=[2*np.pi/spec.Content['pins'],'rad','Pin Pitch Angle']
    spec.loc['I']=[spec.Content['zd']/(spec.Content['zd']-spec.Content['zr']),'','Reduction Ratio']
    spec.loc['Ypin']=[0.0,'mm','Position of Pin']
    if STATE==1:
        spec.loc['m']=[float(values['-m-']),'mm','Module']
        spec.loc['BEARING_FACTOR']=[float(values['-BEARING_FACTOR-']),'','Bearing Factorc']
        spec.loc['PIN_HOLE_FACTOR']=[float(values['-PIN_HOLE_FACTOR-']),'','Pin Hole Factor']
        spec.loc['Rbr']=[spec.Content['m']*spec.Content['zr'],'mm','Radius of Base Circle for Ring']
        spec.loc['Rbd']=[spec.Content['m']*spec.Content['zd'],'mm','Radius of Base Circle for Disc']
        spec.loc['bearing_dia']=[2*spec.Content['Rbd']*spec.Content['BEARING_FACTOR'],'mm','Bearing Diameter']
        spec.loc['pin_hole_dia']=[(spec.Content['Rbd']-spec.Content['bearing_dia']/2)*spec.Content['PIN_HOLE_FACTOR'],'mm','Pin Hole Diameter']
        spec.loc['ea']=[spec.Content['Rbr']-spec.Content['Rbd'],'mm','Actual Eccentricity for Disc']
        spec.loc['pin_dia']=[spec.Content['pin_hole_dia']-2*spec.Content['ea'],'mm','Pin Diameter']
        spec.loc['Xpin']=[(spec.Content['Rbd']+spec.Content['bearing_dia']/2)/2,'mm','Position of Pin']
        spec.loc['Rar']=[spec.Content['Rbr']/spec.Content['zr'],'mm','Radius of Rolling Circle for Ring']
        spec.loc['Rad']=[spec.Content['Rbd']/spec.Content['zd'],'mm','Radius of Rolling Circle for Disc']
    elif STATE==0:
        spec.loc['Rbr']=[float(values['-Rbr-']),'mm','Radius of Base Circle for Ring']
        spec.loc['bearing_dia']=[float(values['-bearing_dia-']),'mm','Bearing Diameter']
        spec.loc['pin_dia']=[float(values['-pin_dia-']),'mm','Pin Diameter']
        spec.loc['Xpin']=[float(values['-Xpin-']),'mm','Position of Pin']
        spec.loc['m']=[spec.Content['Rbr']/spec.Content['zr'],'mm','Module']
        spec.loc['Rar']=[spec.Content['Rbr']/spec.Content['zr'],'mm','Radius of Rolling Circle for Ring']
        spec.loc['Rbd']=[spec.Content['m']*spec.Content['zd'],'mm','Radius of Base Circle for Disc']
        spec.loc['Rad']=[spec.Content['Rbd']/spec.Content['zd'],'mm','Radius of Rolling Circle for Disc']
        spec.loc['ea']=[spec.Content['Rbr']-spec.Content['Rbd'],'mm','Actual Eccentricity for Disc']
        spec.loc['pin_hole_dia']=[spec.Content['pin_dia']+2*spec.Content['ea'],'mm','Pin Hole Diameter']
        spec.loc['BEARING_FACTOR']=[spec.Content['bearing_dia']/(2*spec.Content['Rbd']),'','Bearing Factorc']
        spec.loc['PIN_HOLE_FACTOR']=[spec.Content['pin_hole_dia']/(spec.Content['Rbd']-spec.Content['bearing_dia']/2),'','Pin Hole Factor']
    spec.loc['er']=[spec.Content['Rar']*spec.Content['h'],'mm','Eccentricity for Ring']
    spec.loc['ed']=[spec.Content['Rad']*spec.Content['h'],'mm','Eccentricity for Disc']
    spec.loc['qr']=[(np.pi*spec.Content['Rbr']/spec.Content['zr'])/2,'mm','Radius of Roller for Ring']
    spec.loc['qd']=[(np.pi*spec.Content['Rbd']/spec.Content['zd'])/2,'mm','Radius of Roller for Disc (equidistant distance)']
    spec.loc['input_dia']=[spec.Content['bearing_dia']-2*spec.Content['ea'],'mm','Input Shaft Diameter']

def UpdateValues():
    window['-m-'].update(spec.Content['m'])
    window['-BEARING_FACTOR-'].update(spec.Content['BEARING_FACTOR'])
    window['-PIN_HOLE_FACTOR-'].update(spec.Content['PIN_HOLE_FACTOR'])
    window['-Rbr-'].update(spec.Content['Rbr'])
    window['-bearing_dia-'].update(spec.Content['bearing_dia'])
    window['-pin_dia-'].update(spec.Content['pin_dia'])
    window['-Xpin-'].update(spec.Content['Xpin'])

def UpdateDisabled():
    if values['-module_based-']:
        window['-m-'].update(disabled=False)
        window['-BEARING_FACTOR-'].update(disabled=False)
        window['-PIN_HOLE_FACTOR-'].update(disabled=False)
        window['-Rbr-'].update(disabled=True)
        window['-bearing_dia-'].update(disabled=True)
        window['-pin_dia-'].update(disabled=True)
        window['-Xpin-'].update(disabled=True)
    elif values['-dia_based-']:
        window['-m-'].update(disabled=True)
        window['-BEARING_FACTOR-'].update(disabled=True)
        window['-PIN_HOLE_FACTOR-'].update(disabled=True)
        window['-Rbr-'].update(disabled=False)
        window['-bearing_dia-'].update(disabled=False)
        window['-pin_dia-'].update(disabled=False)
        window['-Xpin-'].update(disabled=False)

def CRD3_PLOT(Xring,Yring,Xdisc,Ydisc):
    # Figure
    fig = plt.figure(figsize=(8,8))
    plt.axes().set_aspect('equal')
    plt.title('Cycloidal Eccentric Reducer Designer 3')
    plt.grid(True)
    # Plot Ring
    circle = np.linspace(0.0,2*np.pi,360)
    plt.plot(spec.Content['Rbr']*np.cos(circle)+spec.Content['X0'],spec.Content['Rbr']*np.sin(circle)+spec.Content['Y0'],':',linewidth=1,color='grey')
    Xring1,Yring1 = Transform(Xring,Yring,spec.Content['X0'],spec.Content['Y0'])
    for i in range(0,int(spec.Content['zr'])):
        Xring2,Yring2 = TransRotation(spec.Content['X0'],spec.Content['Y0'],Xring1,Yring1,i*spec.Content['thetaR'])
        plt.plot(Xring2,Yring2,'-',linewidth=1.5,color='black')
    # Plot Disc
    plt.plot(spec.Content['Rbd']*np.cos(circle)+spec.Content['ea']+spec.Content['X0'],spec.Content['Rbd']*np.sin(circle)+spec.Content['Y0'],':',linewidth=1,color='grey')
    Xdisc1,Ydisc1 = Transform(Xdisc,Ydisc,spec.Content['X0'],spec.Content['Y0'])
    for i in range(0,int(spec.Content['zd'])):
        Xdisc2,Ydisc2 = TransRotation(spec.Content['X0'],spec.Content['Y0'],Xdisc1,Ydisc1,i*spec.Content['thetaD'])
        Xdisc3,Ydisc3 = Transform(Xdisc2,Ydisc2,spec.Content['ea'],0)
        plt.plot(Xdisc3,Ydisc3,'-',linewidth=1.5,color='blue')
    # Bearing on Eccentric Disc
    XX,YY = Circle(spec.Content['bearing_dia'],spec.Content['seg_circle'])
    XX,YY = Transform(XX,YY,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
    plt.plot(XX,YY, '-', linewidth=1.5, color='blue')
    # Input Shaft
    XX,YY = Circle(spec.Content['input_dia'],spec.Content['seg_circle'])
    XX,YY = Transform(XX,YY,spec.Content['X0'],spec.Content['Y0'])
    plt.plot(XX,YY, '-', linewidth=1.5, color='black')
    # Pin holes on Eccentric Disc
    for i in range(0,int(spec.Content['pins'])):
        XX,YY = Circle(spec.Content['pin_hole_dia'],spec.Content['seg_circle'])
        XX,YY = Transform(XX,YY,spec.Content['Xpin'],spec.Content['Ypin'])
        XX2,YY2 = Rotation(XX,YY,spec.Content['angle_pins'],i)
        XX2,YY2 = Transform(XX2,YY2,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
        plt.plot(XX2,YY2, '-', linewidth=1.5, color='blue')
    # Pin on Output Shaft
    for i in range(0,int(spec.Content['pins'])):
        XX,YY = Circle(spec.Content['pin_dia'],spec.Content['seg_circle'])
        XX,YY = Transform(XX,YY,spec.Content['Xpin'],spec.Content['Ypin'])
        XX2,YY2 = Rotation(XX,YY,spec.Content['angle_pins'],i)
        XX2,YY2 = Transform(XX2,YY2,spec.Content['X0'],spec.Content['Y0'])
        plt.plot(XX2,YY2, '-', linewidth=1.5, color='orange')
    # Annotate
    Cheight = 1.2*spec.Content['Rbd']/len(spec)
    Nrow = len(spec)*Cheight
    for i in range(0,len(spec)):
        plt.text(spec.Content['X0'],spec.Content['Y0']+Nrow/2-Cheight*i,"%s = %s[%s], %s"%(spec.index[i],spec.Content[i],spec.Unit[i],spec.Remark[i]),verticalalignment='center', horizontalalignment='center', color='black', fontsize="x-small")
    # Figure
    Result = os.path.join(spec.Content['WorkingDirectory'], f'Result.png')
    plt.savefig(Result,dpi=100)
    plt.show()

def SaveDXF(Xring,Yring,Xdisc,Ydisc):
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()
    # Tooth of Disc
    Xdisc1,Ydisc1 = Transform(Xdisc,Ydisc,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
    cpoint1D = [(Xdisc1[0],Ydisc1[0])]
    for i in range(0,len(Xdisc1)) :
        cpoint1D.append((Xdisc1[i],Ydisc1[i]))
    if values['-spline-']:
        msp.add_spline(cpoint1D,dxfattribs={'color':4})
    else:
        msp.add_polyline2d(cpoint1D,dxfattribs={'color':4})
    # Tooth of Ring Gear
    Xring1,Yring1 = Transform(Xring,Yring,spec.Content['X0'],spec.Content['Y0'])
    cpoint1R = [(Xring1[0],Yring1[0])]
    for i in range(0,len(Xring1)) :
        cpoint1R.append((Xring1[i],Yring1[i]))
    if values['-spline-']:
        msp.add_spline(cpoint1R)
    else:
        msp.add_polyline2d(cpoint1R)
    # Base Circles
    msp.add_circle((spec.Content['X0']+spec.Content['ea'],spec.Content['Y0']),radius=spec.Content['Rbd'],dxfattribs={'color':4})
    msp.add_circle((spec.Content['X0'],spec.Content['Y0']),radius=spec.Content['Rbr'],dxfattribs={'color':0})
    # Bearing Circles
    msp.add_circle((spec.Content['X0']+spec.Content['ea'],spec.Content['Y0']),radius=spec.Content['bearing_dia']/2,dxfattribs={'color':4})
    msp.add_circle((spec.Content['X0'],spec.Content['Y0']),radius=spec.Content['input_dia']/2)
    # Pin holes
    X_pinhole_cen1 = spec.Content['X0']+spec.Content['Xpin']+spec.Content['ea']
    Y_pinhole_cen1 = spec.Content['Y0']+spec.Content['Ypin']
    X_pinhole_cen2,Y_pinhole_cen2 = Transform(X_pinhole_cen1,Y_pinhole_cen1,-spec.Content['X0']-spec.Content['ea'],-spec.Content['Y0'])
    for i in range(0,spec.Content['pins']):
        X_pinhole_cen3,Y_pinhole_cen3 = Rotation(X_pinhole_cen2,Y_pinhole_cen2,spec.Content['angle_pins'],i)
        X_pinhole_cen4,Y_pinhole_cen4 = Transform(X_pinhole_cen3,Y_pinhole_cen3,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
        msp.add_circle((X_pinhole_cen4,Y_pinhole_cen4),radius=spec.Content['pin_hole_dia']/2,dxfattribs={'color':4})
    # Pins
    X_pin_cen1 = spec.Content['X0']+spec.Content['Xpin']
    Y_pin_cen1 = spec.Content['Y0']+spec.Content['Ypin']
    X_pin_cen2,Y_pin_cen2 = Transform(X_pin_cen1,Y_pin_cen1,-spec.Content['Y0'],-spec.Content['Y0'])
    for i in range(0,spec.Content['pins']):
        X_pin_cen3,Y_pin_cen3 = Rotation(X_pin_cen2,Y_pin_cen2,spec.Content['angle_pins'],i)
        X_pin_cen4,Y_pin_cen4 = Transform(X_pin_cen3,Y_pin_cen3,spec.Content['X0'],spec.Content['Y0'])
        msp.add_circle((X_pin_cen4,Y_pin_cen4),radius=spec.Content['pin_dia']/2,dxfattribs={'color':6})
    # Deco for Ring Gear
    thickness = 2*spec.Content['m']
    X_START_RING = spec.Content['Rbr']+thickness+spec.Content['X0']
    Y_START_RING = spec.Content['Y0']
    X_END_RING = Xring1[0]
    Y_END_RING = spec.Content['Y0']
    msp.add_line([X_START_RING,Y_START_RING],[X_END_RING,Y_END_RING])
    X_START_RING2,Y_START_RING2 = Transform(X_START_RING,Y_START_RING,-spec.Content['X0'],-spec.Content['Y0'])
    X_START_RING3,Y_START_RING3 = Rotation(X_START_RING2,Y_START_RING2,2*np.pi/spec.Content['zr'],1)
    X_START_RING4,Y_START_RING4 = Transform(X_START_RING3,Y_START_RING3,spec.Content['X0'],spec.Content['Y0'])
    X_END_RING2,Y_END_RING2 = Transform(X_END_RING,Y_END_RING,-spec.Content['X0'],-spec.Content['Y0'])
    X_END_RING3,Y_END_RING3 = Rotation(X_END_RING2,Y_END_RING2,2*np.pi/spec.Content['zr'],1)
    X_END_RING4,Y_END_RING4 = Transform(X_END_RING3,Y_END_RING3,spec.Content['X0'],spec.Content['Y0'])
    msp.add_line([X_START_RING4,Y_START_RING4],[X_END_RING4,Y_END_RING4])
    msp.add_arc(center=(spec.Content['X0'],spec.Content['Y0']), radius=spec.Content['Rbr']+thickness, start_angle=0, end_angle=360/spec.Content['zr'])
    # Deco for Eccentric Disc
    X_START_DISC = spec.Content['Rbd']-thickness+spec.Content['X0']+spec.Content['ea']
    Y_START_DISC = spec.Content['Y0']
    X_END_DISC = Xdisc1[0]
    Y_END_DISC = spec.Content['Y0']
    msp.add_line([X_START_DISC,Y_START_DISC],[X_END_DISC,Y_END_DISC],dxfattribs={'color':4})
    X_START_DISC2,Y_START_DISC2 = Transform(X_START_DISC,Y_START_DISC,-spec.Content['X0']-spec.Content['ea'],-spec.Content['Y0'])
    X_START_DISC3,Y_START_DISC3 = Rotation(X_START_DISC2,Y_START_DISC2,2*np.pi/spec.Content['zd'],1)
    X_START_DISC4,Y_START_DISC4 = Transform(X_START_DISC3,Y_START_DISC3,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
    X_END_DISC2,Y_END_DISC2 = Transform(X_END_DISC,Y_END_DISC,-spec.Content['X0']-spec.Content['ea'],-spec.Content['Y0'])
    X_END_DISC3,Y_END_DISC3 = Rotation(X_END_DISC2,Y_END_DISC2,2*np.pi/spec.Content['zd'],1)
    X_END_DISC4,Y_END_DISC4 = Transform(X_END_DISC3,Y_END_DISC3,spec.Content['X0']+spec.Content['ea'],spec.Content['Y0'])
    msp.add_line([X_START_DISC4,Y_START_DISC4],[X_END_DISC4,Y_END_DISC4],dxfattribs={'color':4})
    msp.add_arc(center=(spec.Content['X0']+spec.Content['ea'],spec.Content['Y0']), radius=spec.Content['Rbd']-thickness, start_angle=0, end_angle=360/spec.Content['zd'] ,dxfattribs={'color':4})
    # Output
    Result = os.path.join(spec.Content['WorkingDirectory'], f'Result.dxf')
    doc.saveas(Result)

##############################
# GUI
sg.theme('Default')
col = [[sg.Text('Working Directory :',size=(15,1)),sg.Input('./Result/',key='-WorkingDirectoty-',size=(30,1)), sg.FolderBrowse()],
        [sg.Text('# Input Mode : ',size=(12,1)),sg.Radio('Module_based','RADIO2',key='-module_based-',default=True,enable_events=True,size=(12,1)),sg.Radio('Dia_based','RADIO2',key='-dia_based-',enable_events=True,size=(12,1)),sg.Button('Update')],
        [sg.Text('Module, m =',size=(32,1)),sg.Input(1.0,key='-m-',size = (10,1)),sg.Text('[mm], (>0)')],
        [sg.Text('Radius of Base Circle for Ring, Rbr =',size=(32,1)),sg.Input(40.0,key='-Rbr-',size=(10,1),disabled=True),sg.Text('[mm]')],
        [sg.Text('Number of Teeth Ring, zr =',size=(32,1)),sg.Input(40,key='-zr-',size=(10,1)),sg.Text('[ea], (Even Number)')],
        [sg.Text('Diff. of Ring and Disc, ze =',size=(32,1)),sg.Input(1,key='-ze-',size=(10,1)),sg.Text('[ea]')],
        [sg.Text('Teeth Height Factor, h =',size=(32,1)),sg.Input(0.7,key='-h-',size=(10,1)),sg.Text('(0~1)')],
        [sg.Text('Control Points for One Tooth, point =',size = (32,1)),sg.Input(50,key='-point-',size=(10,1)),sg.Text('[ea]')],
        [sg.Text('Center Position, X0 =',size=(32,1)),sg.Input(0.0,key='-X0-',size=(10,1)),sg.Text('[mm]')],
        [sg.Text('Center Position, Y0 =',size=(32,1)),sg.Input(0.0,key='-Y0-',size=(10,1)),sg.Text('[mm]')],
        [sg.Text('Bearing Size Factor =',size=(32,1)),sg.Input(0.6,key='-BEARING_FACTOR-',size=(10,1)),sg.Text('(0~1)')],
        [sg.Text('Pin Hole Size Factor =',size=(32,1)),sg.Input(0.6,key='-PIN_HOLE_FACTOR-',size=(10,1)),sg.Text('(0~1)')],
        [sg.Text('Bearing Diameter =',size=(32,1)),sg.Input(46.8,key='-bearing_dia-',size=(10,1),disabled=True),sg.Text('[mm]')],
        [sg.Text('Pin Diameter =',size=(32,1)),sg.Input(7.36,key='-pin_dia-',size=(10,1),disabled=True),sg.Text('[mm]')],
        [sg.Text('Pin Position, Xpin =',size=(32,1)),sg.Input(31.2,key='-Xpin-',size=(10,1),disabled=True),sg.Text('[mm]')],
        [sg.Text('Number of Pins, pins =',size=(32,1)),sg.Input(16,key='-pins-',size=(10,1)),sg.Text('[ea]')],
        [sg.Text('# DXF Output Option : '),sg.Radio('Spline','RADIO1',key='-spline-',default=True),sg.Radio('Polyline','RADIO1',key='-polyline-')],
        [sg.Button('Run'),sg.Button('Exit')]]

layout = [[col]]
window = sg.Window('CRD3',layout,icon="CRD3.ico")

spec = pd.DataFrame(columns=['Parameter','Content','Unit','Remark'])
spec = spec.set_index('Parameter')

while True:
    event,values=window.read()
    if event in (sg.WIN_CLOSED,'Exit'):
        break
    elif event=='Run':
        Update()
        # Hypocycloid-like Tooth of Ring
        Xring,Yring,alphaR,betaR,phiR = HypoTooth(spec.Content['thetaR'],spec.Content['point'],spec.Content['Rar'],spec.Content['Rbr'],spec.Content['er'],spec.Content['qr'])
        # Hypocycloid-like Tooth of Disc
        Xdisc,Ydisc,alphaD,betaD,phiD = HypoTooth(spec.Content['thetaD'],spec.Content['point'],spec.Content['Rad'],spec.Content['Rbd'],spec.Content['ed'],spec.Content['qd'])
        os.makedirs(spec.Content['WorkingDirectory'],exist_ok=True)
        Result = os.path.join(spec.Content['WorkingDirectory'],f'Result.csv')
        spec.to_csv(Result,header=True,index=True)
        SaveDXF(Xring,Yring,Xdisc,Ydisc)
        CRD3_PLOT(Xring,Yring,Xdisc,Ydisc)
    elif event=='Update':
        if values['-module_based-']:
            Parameters(1)
            UpdateValues()
        elif values['-dia_based-']:
            Parameters(0)
            UpdateValues()
        UpdateValues()
    elif values['-module_based-']:
        Parameters(0)
        UpdateValues()
        UpdateDisabled()
    elif values['-dia_based-']:
        Parameters(1)
        UpdateValues()
        UpdateDisabled()
window.close()
