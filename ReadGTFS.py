import csv
import geopy.distance
from shapely.geometry import LineString, Point
import time

class parseGTFS:
    def __init__(self,trip_files):
        self.trip_files = trip_files
    def readCSV(self, file_name):
        csv_file = open(file_name, mode='r')
        data = csv.DictReader(csv_file)
        return data
    def toElapsedTime(self, date_time, current_date):
        time_current = time.mktime(time.strptime(current_date,"%d/%m/%Y"))
        date_time = date_time.split(":")
        time_midnight = 3600*int(date_time[0]) + 60*int(date_time[1]) + int(date_time[2])
        return time_current + time_midnight
    def parseTrips(self):
        trips = parseGTFS(trip_files)
        trips_data = trips.readCSV(self.trip_files[8])
        line_count=0
        trip_set=set()
        trajectories=[]
        stop_dict={}
        for row in trips_data:
            prev_len=len(trip_set)
            trip_set.add(row["trip_id"])
            new_len=len(trip_set)
            if (prev_len!=new_len):
                trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[6])
        for row in stops_data:
            stop_dict[row["stop_id"]] = (row["stop_lat"],row["stop_lon"])
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        calendar = parseGTFS(trip_files)
        calendar_data = calendar.readCSV(self.trip_files[2])
        flag=0
        prev_trip_id=0
        counter=0
        for row in stop_times_data:
            if counter<5000:
                if prev_trip_id==row["trip_id"] or flag==0:
                    traj_dict={}
                    val = self.toElapsedTime(row["arrival_time"],"08/02/2019")
                    traj_dict[val] = (stop_dict[row["stop_id"]])
                    for traj in trajectories:
                        if traj.trip_id==row["trip_id"]:
                            traj.trajectory.append(traj_dict)
                            traj.stops.append(row["stop_id"])
                            break
                else:
                    traj_dict={}
                    val = self.toElapsedTime(row["arrival_time"],"08/02/2019")
                    traj_dict[val] = (stop_dict[row["stop_id"]])
                    for traj in trajectories:
                        if traj.trip_id==row["trip_id"]:
                            traj.trajectory.append(traj_dict)
                            traj.stops.append(row["stop_id"])
                            break
            else:
                break
            prev_trip_id=row["trip_id"]
            flag=1
            counter+=1
        for traj in trajectories:
            print len(traj.trajectory)
        shapes = parseGTFS(trip_files)
        shapes_data = shapes.readCSV(self.trip_files[4])
        for traj in trajectories:
            for i in range(len(traj.stops)):
                flag=0
                minseq=0
                for row in shapes_data:
                    if row["shape_id"]==traj.shapeid:
                        if flag==0:
                            prev_row=row
                            flag=1
                            min_dist=0
                        else:
                            dist=abs((geopy.distance.geodesic(stop_dict[traj.stops[i]], (row["shape_pt_lat"], row["shape_pt_lon"])).km+geopy.distance.geodesic(stop_dict[traj.stops[i]], (prev_row["shape_pt_lat"], prev_row["shape_pt_lon"])).km)**2 - (geopy.distance.geodesic((row["shape_pt_lat"], row["shape_pt_lon"]), (prev_row["shape_pt_lat"], prev_row["shape_pt_lon"])).km)**2)
                            if min_dist==0:
                                min_dist=dist
                            elif dist<min_dist:
                                min_dist=dist
                                minseq=int(row["shape_pt_sequence"])
                    elif row["shape_id"]!=traj.shapeid and flag==1:
                        break
                traj.proj.append(minseq)
        for traj in trajectories:
            for i in range(len(traj.stops)):
                for row in shapes_data:
                    if (traj.proj[i]-1)==int(row["shape_pt_sequence"]):
                        prev_row = row
                    elif traj.proj[i]==int(row["shape_pt_sequence"]):
                        line = LineString([(prev_row["shape_pt_lat"], prev_row["shape_pt_lon"]), (row["shape_pt_lat"], row["shape_pt_lon"])])
                        p = Point(stop_dict[traj.stops[i]])
                        np = line.interpolate(line.project(p))
                        traj.stop_proj.append(np)
                        break
        for traj in trajectories:
            traj.getPosition(20)
        return trajectories

class Trajectory:
    def __init__(self,trip_id,service_id,shape_id):
        self.trip_id=trip_id
        self.service_id=service_id
        self.shapeid=shape_id
        self.trajectory=[]
        self.stops=[]
        self.proj=[]
        self.stop_proj=[]
    def getPosition(self, time):
        for i in range(len(self.stop_proj)):
            print self.stop_proj[i]
        first_stop_x = 1
        first_stop_y = 2
        second_stop_x = 3
        second_stop_y = 4
        time_first = 5
        time_second =6
        posx = first_stop_x + ((time-time_first)*(second_stop_x-first_stop_x))/(time_second-time_first)
        posy = first_stop_y + ((time-time_first)*(second_stop_y-first_stop_y))/(time_second-time_first)
        return (posx, posy)
    def isActive(self, time):
        return isvActive

class Transit:
    def __init__(self,file_name,trajectories):
        self.file_name=file_name
        self.trajectories=trajectories
    def activeTrajectories(self, time):
        return allActiveTrajectories

trip_files = ["../NYC/agency.txt", "../NYC/calendar_dates.txt", "../NYC/calendar.txt", "../NYC/routes.txt", "../NYC/shapes.txt", "../NYC/stop_times.txt", "../NYC/stops.txt", "../NYC/transfers.txt", "../NYC/trips.txt"]
inst = parseGTFS(trip_files)
inst_data = inst.parseTrips()
