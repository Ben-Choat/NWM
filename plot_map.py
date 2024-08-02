import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gp

def plot_map_bymodel(Selected_calibration,All_Stats,stats,title,output_figure,MinModels,MinThreshold):
    import math as m
    # Model_RR=['NWM2.1',"CFE","CFE_X","Topmodel"]
    Model_RR=["CFE","CFE_X","Topmodel"]

    if(stats=='KGE') | (stats=='NNash'):


#         All_Stats = All_Stats.query("Model_RR in @Model_RR")
#         print(f'All_Stats head after query: {All_Stats.head()}')
                        
        Selected_calibration['Best']=''
        Selected_calibration['Dif']=-9
        print(f'unique(All_Stats.ModelRR): {All_Stats.Model_RR.unique()}')
        for i in range (0,len(Selected_calibration)):

            hru_id=Selected_calibration.index[i]
            Temp=All_Stats[All_Stats.index==hru_id]
            try:
                TEMP_NWM = Temp[Temp['Model_RR']=='NWM2.1'][stats].values[0]

            except Exception as e:
                print(e)
                continue

#             Temp = Temp.query("Model_RR in @Model_RR")

            print(f'hru_id: {hru_id}')
            # print(f'Temp: {Temp}')
#             print(f'len Temp: {len(Temp)}')
 
            print(f'len(Temp): {len(Temp)}')

            if(len(Temp)>=MinModels):
                Temp = Temp.query("Model_RR in @Model_RR")

                Temp=Temp.sort_values(by=[stats],ascending=False)
#                print(Temp)
                # with open('/test.txt', 'a') as f:
                #    f.write(print(Temp))
#                 Temp.to_csv('./test.txt', mode='a')
                print(Temp.iloc[0]['Model_RR'])
                Selected_calibration.at[hru_id,'Best']=Temp.iloc[0]['Model_RR']
                # if(Temp.iloc[0]['Model_RR']=='NWM2.1'):
                 #    Selected_calibration.at[hru_id,'Dif']=abs(Temp.iloc[0][stats]-Temp.iloc[1:4][stats].max())

                # else:
                Selected_calibration.at[hru_id,'Dif']=abs(Temp.iloc[0][stats]-TEMP_NWM)

            else:
                print(f'less than {MinModels}, so continuing')
                continue


    nmodels=len(Model_RR)
    nrow=m.ceil(nmodels/2)
    #figsize=(nrow*4, ncols*3)
    if nmodels > 3:
        f, axes = plt.subplots(figsize=(16, 9.5), ncols=2, nrows=nrow)
        # define locations for annotations
        text_loc = {
                    0: [0.15, 0.65],
                    1: [0.55, 0.65],
                    2: [0.15, 0.4],
                    3: [0.55, 0.4],
                    4: [0.15, 0.15],
                    5: [0.55, 0.15]
                    }
    else:
        f, axes = plt.subplots(figsize=(8, 9.5), ncols=1, nrows=len(Model_RR))
    # define locations for annotations
        text_loc = {
                    0: [0.2, 0.67, '(a)'],
                    1: [0.2, 0.4, '(b)'],
                    2: [0.2, 0.13, '(c)']
                    }


    us_states_file="/home/west/us_states.json"
    us_states = gp.read_file(us_states_file)
    us_states=us_states[us_states.name != "Alaska"]
    us_states_bounds = us_states.geometry.total_bounds


    for i, ax in enumerate(axes.flatten()):
        xtext = text_loc[i][0]
        ytext = text_loc[i][1]
        annot_in = text_loc[i][2]

        us_states.plot(ax=ax,color='silver', edgecolor='white', linewidth=1, zorder=0)

        All_Models_temp=All_Stats[All_Stats['Model_RR']==Model_RR[i]]
                                                                        
        CAMELS_516_temp=Selected_calibration[
                (Selected_calibration['Best']==Model_RR[i]) & \
                        (Selected_calibration['Dif']>=MinThreshold)]

   
        im=ax.scatter(All_Models_temp['Long'],All_Models_temp['Lat'],s=60,
                   c=All_Models_temp[stats],vmin=0,vmax=1,cmap='Spectral');
        if(Model_RR[i]=="Topmodel"): Model_RR_str="TOPMODEL"
        else: Model_RR_str=Model_RR[i]
        ax.set_title(Model_RR_str, fontsize=13,weight='bold')
  
        ax.scatter(CAMELS_516_temp['Long'],
                    CAMELS_516_temp['Lat'],
                    s=70, facecolors='none', # s=110
                    edgecolors='black',
                    linewidth=1.5)

        #All_Models_temp=All_Models_temp.loc[['10244950','05591550','10336660','09306242']]
        #axes[ax1][ax2].scatter(All_Models_temp['Long'],All_Models_temp['Lat'],s=350, facecolors='none', edgecolors='green',linewidth=2)


        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_xlim(([-125,-65]))
        ax.set_ylim(([25,50]))
        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)

        # add annotations
        plt.figtext(xtext, ytext, annot_in, fontsize = 15)




        #plt.title(models[i])
        #plt.figtext(xtext,ytext,models[i],fontsize=10)

    cbar_ax = f.add_axes([0.8, 0.15, 0.02, 0.7])
    f.colorbar(im, cax=cbar_ax).set_label(label=stats,size=15,weight='bold')
    f.savefig(output_figure, bbox_inches='tight',dpi=300)


Results_calibration = "/media/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Calib_plots_WithNoah"

All_Stats = pd.read_csv(f"{Results_calibration}/NWM_performance_first.csv",
                        dtype={'hru_id_CAMELS': 'string'},                       
                         ).drop_duplicates(
                                subset=['hru_id_CAMELS', 'Model']
                         ).reset_index(
                                 drop = True
                                 ).set_index('hru_id_CAMELS')

#NOTE THAT THE NAME OF THE FILE TO BE READ IN FOR SELECTED_CALIBRATINO, CHANGES BASED 
# ON TIME WRITTEN
Selected_calibration = pd.read_csv(f"{Results_calibration}/AllBasins2024-05-171248.csv",
                        dtype={'hru_id_CAMELS': 'string'}).set_index('hru_id_CAMELS')


# print(f'All_Stats head: {All_Stats.head()}')
# print(f'Selected_calibration head: {Selected_calibration.head()}')


MinModels=4

title="KGE - multiple models"

# print(All_Stats)

All_Stats_4=All_Stats.copy()
drop=[]
Unique_index=All_Stats.index.unique()
print(f'unique_index: {Unique_index}')
for i in range (0,len(All_Stats.index.unique())):
    hru_id=Unique_index[i]
    Temp=All_Stats[All_Stats.index==hru_id]
    if(len(Temp)<MinModels):
        drop.append(hru_id)

stats="KGE"
All_Stats_4=All_Stats_4.drop(drop)
#print(All_Stats)
MinThreshold=0.0
# 
output_figure=Results_calibration+"/RR_"+stats+"map_"+str(MinModels)+"NoMarkup_woNWM21.png"
plot_map_bymodel(Selected_calibration,All_Stats_4,stats,title,output_figure,MinModels,MinThreshold)
MinThreshold=0.05
# 
output_figure=Results_calibration+"/RR_"+stats+"map_"+str(MinModels)+"NoMarkupTh_005_woNWM21.png"
plot_map_bymodel(Selected_calibration,All_Stats_4,stats,title,output_figure,MinModels,MinThreshold)


stats="NNash"
output_figure=Results_calibration+"/RR_"+stats+"map_"+str(MinModels)+"NoMarkup_woNWM21.png"
title="NNSE - multiple models"
MinThreshold=0
plot_map_bymodel(Selected_calibration,All_Stats_4,stats,title,output_figure,MinModels,MinThreshold)


