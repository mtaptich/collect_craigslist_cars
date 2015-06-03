import os, sys
lib_path = os.path.abspath('scripts/')
sys.path.append(lib_path)
import craigslist_cars as cc, email_csv as ec
import pandas as pd
import time

def CSVtoDB(path):
	db = pd.read_csv(path)
	db.rename(columns = lambda x: x.replace(' ', '_').lower(), inplace=True)
	return db

def quick_update(make, model):
	df = levalized_cost(make, model)
	df.to_csv('output/'+make+'_'+model+'_'+time.strftime("%d_%m_%Y")+'.csv', sep=',', index=False, encoding='utf-8')
	ec.send('output/'+make+'_'+model+'_'+time.strftime("%d_%m_%Y")+'.csv',make, model, emailto="meholleran@gmail.com")

def pull_mpg(make, model, year):
	a = specs[(specs['make'] == make) & (specs['year'] == year) & (specs['model'].str.contains(model))]
	return a.comb08.mean()

def remaining_life(odometer, annual_mileage, max_odometer):
	"""
	We only want to own a car for 10 years max
	"""
	try:
		lifetime = (max_odometer - float(odometer)) / annual_mileage; 
		if lifetime < 10:
			return max_odometer - float(odometer), lifetime
		else:
			return max_odometer - float(odometer), 10 
	except:
		return None,None

def monthly_cost(price, interest, initial_investment, payment_years):
	try: 
		monthly_interest = (1 + interest)**(1.0/12) - 1; 
		upfront_cost = float(price)-initial_investment+float(price)*0.1; 
		exp= payment_years*12;
		monthly_cost = ( upfront_cost  * monthly_interest * (1 + monthly_interest)**exp ) / ( (1 + monthly_interest)**exp - 1 );
		return  round(monthly_cost,1)  # return monthly value
	except:
		return ""

def levalized_cost(make, model, annual_mileage=5000, max_odometer=180000, fuel_cost=3.5, interest=0.04, initial_investment= 4500, payment_years=5):
	"""
	A tool to screen Craigslist for cars and returns levalized cost of ownership. 
	
	"""

	# Screen Craigslist for 
	df = cc.query("sfbay", 1000, make, model)

	# Pull the combined MPG for the cars of interest
	df["mpg"] = df["YEAR"].map(lambda x: pull_mpg(make, model, int(x)))

	# How many miles and years remain for this vehicle
	df["miles_remaining"], df["years_remaining"] = zip(*df["odometer"].map(lambda x: remaining_life(x,annual_mileage, max_odometer)))

	# What will it cost to operate this vehicle per year, assuming a uniform annual VMT and constant 
	df["_monthly_operating_cost"] = df["mpg"]**(-1) * fuel_cost * annual_mileage / 12;

	# What will be the levelized annual cost associated with capital expenses
	df["_monthly_capital_cost"] = df["PRICE"].map(lambda x: monthly_cost(x, interest, initial_investment, payment_years)) 

	# What is the estimated monthly cost
	df["_total_monthly_cost"] = (df["_monthly_operating_cost"] + df["_monthly_capital_cost"]);

	# Assign Make and Model
	df["_make"] = make;
	df["_model"] = model;
	df["URL"] = df["url"]
	df = df.drop('url', 1)

	df = df.reindex_axis(sorted(df.columns), axis=1)

	df.to_csv('output/'+make+'_'+model+'_'+time.strftime("%d_%m_%Y")+'.csv', sep=',', index=False, encoding='utf-8')

	return df


if __name__ == "__main__":
    try:
    	specs = CSVtoDB("data/vehicle_MPG_1984_2015.csv")[['make','model', 'year', 'comb08', 'city08', 'highway08']]
    	
    	### Update tuples of car brand
    	SearchVehicles = [("Audi", "A3"), ("Subaru", "Outback"), ("Audi", "A4"), ("BMW", "3 Series"), ("Volkswagen", "Jetta"), ('Subaru', 'Forester'),('Subaru', 'Impreza'), ('Subaru', 'XV Crosstrek')]
    	
    	for veh in SearchVehicles:
    		print veh[0], veh[1]
    		try:
    			df = levalized_cost(veh[0], veh[1]);
    			df_master = df_master.append(df, ignore_index=True)
    			df = None
    		except:
    			df = levalized_cost(veh[0], veh[1]);
    			df_master = df
    			df = None

    	df_master = df_master.sort_index(by=['time_posted','_total_monthly_cost'], ascending=[False, True])
    	df_master.to_csv('output/master_list_'+time.strftime("%d_%m_%Y")+'.csv', sep=',', index=False, encoding='utf-8')
    	ec.send('output/master_list_'+time.strftime("%d_%m_%Y")+'.csv', "m.taptich@gmail.com")


    except KeyboardInterrupt:
        pass




