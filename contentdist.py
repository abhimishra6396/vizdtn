import csv
import geopy.distance
from shapely.geometry import LineString, Point
import time
import operator
from collections import defaultdict, namedtuple
import matplotlib.pyplot as plt
import numpy as np

class Graph:
    def __init__(self, list_tuple):
        self.list_tuple=list_tuple

    def min_spanning_arborescence(self, arcs, sink):
        good_arcs = []
        quotient_map = {arc.tail: arc.tail for arc in arcs}
        quotient_map[sink] = sink
        while True:
            min_arc_by_tail_rep = {}
            successor_rep = {}
            for arc in arcs:
                if arc.tail == sink:
                    continue
                tail_rep = quotient_map[arc.tail]
                head_rep = quotient_map[arc.head]
                if tail_rep == head_rep:
                    continue
                if tail_rep not in min_arc_by_tail_rep or min_arc_by_tail_rep[tail_rep].weight > arc.weight:
                    min_arc_by_tail_rep[tail_rep] = arc
                    successor_rep[tail_rep] = head_rep
            cycle_reps = self.find_cycle(successor_rep, sink)
            if cycle_reps is None:
                good_arcs.extend(min_arc_by_tail_rep.values())
                return self.spanning_arborescence(good_arcs, sink)
            good_arcs.extend(min_arc_by_tail_rep[cycle_rep] for cycle_rep in cycle_reps)
            cycle_rep_set = set(cycle_reps)
            cycle_rep = cycle_rep_set.pop()
            quotient_map = {node: cycle_rep if node_rep in cycle_rep_set else node_rep for node, node_rep in quotient_map.items()}

    def find_cycle(self, successor, sink):
        visited = {sink}
        for node in successor:
            cycle = []
            while node not in visited:
                visited.add(node)
                cycle.append(node)
                node = successor[node]
            if node in cycle:
                return cycle[cycle.index(node):]
        return None

    def spanning_arborescence(self, arcs, sink):
        arcs_by_head = defaultdict(list)
        for arc in arcs:
            if arc.tail == sink:
                continue
            arcs_by_head[arc.head].append(arc)
        solution_arc_by_tail = {}
        stack = arcs_by_head[sink]
        while stack:
            arc = stack.pop()
            if arc.tail in solution_arc_by_tail:
                continue
            solution_arc_by_tail[arc.tail] = arc
            stack.extend(arcs_by_head[arc.tail])
        return solution_arc_by_tail

class parseGTFS(Graph):
    def __init__(self,trip_files):
        self.trip_files = trip_files
        self.start_time = 12*3600
        self.visited_count = 0
        self.time_taken = 0
    def readCSV(self, file_name):
        csv_file = open(file_name, mode='r')
        data = csv.DictReader(csv_file)
        return data
    def toElapsedTime(self, date_time):
        date_time=date_time.split(":")
        time_midnight = 3600*int(date_time[0]) + 60*int(date_time[1]) + int(date_time[2])
        return time_midnight
    def parseTrips(self, day, content_transfer_time):
        calendar = parseGTFS(trip_files)
        calendar_data = calendar.readCSV(self.trip_files[2])
        trips = parseGTFS(trip_files)
        trips_data = trips.readCSV(self.trip_files[8])
        trip_set=set()
        trajectories=[]
        stop_dict={} #stop id to location and details mapping
        stop_index_dict={} #stop id to it's index in stop_dict
        trip_dict={} #trip id to route id mapping
        route_dict={} #route id to all it's contained multi route stops
        route_ordered_dict={} #route id to it's stops in order
        trip_service_dict={} #trip id to bool suggesting if that trip was present 
        ind_array=[]
        wkd=0
        i=0
        flag=0
        if day in ["monday","tuesday","wednesday","thursday","friday"]:
            wkd=1
        for row in trips_data:
            trip_dict[row["trip_id"]]=row["route_id"]
            trip_service_dict[row["trip_id"]]=0
            if wkd==1:
                if row["service_id"]=="1":
                    trip_set.add(row["trip_id"])
                    trip_service_dict[row["trip_id"]]=1
                    trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
            else:
                if day=="saturday":
                    if row["service_id"]=="2":
                        trip_set.add(row["trip_id"])
                        trip_service_dict[row["trip_id"]]=1
                        trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
                else:
                    if row["service_id"]=="3":
                        trip_set.add(row["trip_id"])
                        trip_service_dict[row["trip_id"]]=1
                        trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
        print "Number of Trips this day is: %d\n" %len(trip_set)
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[6])
        for row in stops_data:
            stop_dict[row["stop_id"]] = [row["stop_lat"],row["stop_lon"],0,0,set()]
            stop_index_dict[row["stop_id"]] = i
            i+=1
        print "Number of Stops in this transport system is: %d\n" %len(stop_dict)
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if int(row["stop_sequence"])==1:
                    stop_dict[row["stop_id"]][2]+=1
        stop_freq = sorted(stop_dict.items(), key=lambda x: x[1][2], reverse=True)
        print "Most Frequent stop for trip to start is: %d which is visited %d times.\n" %(int(stop_freq[0][0]), int(stop_freq[0][1][2]))
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        count=0
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if len(stop_dict[row["stop_id"]][4])==0:
                        stop_dict[row["stop_id"]][4].add((trip_dict[row["trip_id"]]))
                elif ~(trip_dict[row["trip_id"]] in stop_dict[row["stop_id"]][4]):
                        stop_dict[row["stop_id"]][4].add((trip_dict[row["trip_id"]]))
                if len(stop_dict[row["stop_id"]][4])>1:
                    stop_dict[row["stop_id"]][3]=1
        route_keys=[]
        print "\n\n\n\n\n\n\n\n\n\n"
        print "Stops with multiple routes are:\n"
        for key in stop_dict.keys():
            if stop_dict[key][3]==1:
                print "Stop ID: ",key,"\tRoutes: ",list(stop_dict[key][4])
                route_keys.append(key)
                count+=1
        print "There are %d Stops that have multiple routes" %count
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        adja_M = [[0 for x in range(len(stop_dict))]for x in range(len(stop_dict))]
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if flag==0:
                    prev_stopID=row["stop_id"]
                    prev_tripID=row["trip_id"]
                    flag=1
                else:
                    if prev_tripID==row["trip_id"]:
                        adja_M[stop_index_dict[prev_stopID]][stop_index_dict[row["stop_id"]]]=1
                    else:
                        prev_stopID=row["stop_id"]
                        prev_tripID=row["trip_id"]
        """for i in range(len(route_keys)):
            ind_array.append(stop_index_dict[route_keys[i]])
        for i in range(len(stop_dict)):
            for j in range(len(stop_dict)):
                if ~(i in ind_array):
                    adja_M[i][j]=0"""
        routes = parseGTFS(trip_files)
        routes_data = trips.readCSV(self.trip_files[3])
        for row in routes_data:
            route_dict[row["route_id"]]=[]
            route_ordered_dict[row["route_id"]]=[]
            for keys in route_keys:
                if row["route_id"] in list(stop_dict[keys][4]):
                    route_dict[row["route_id"]].append(keys)
        routes_data = trips.readCSV(self.trip_files[3])
        print "\n\n\n\n\n\n\n\n\n\n"
        print "The list of Routes and their multi-route stops are:\n"
        for row in routes_data:
            print "Route: ", row["route_id"],"\tStops: ",route_dict[row["route_id"]]
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        flag=0
        temp=[]
        print "\n\n\n\n\n\n\n\n\n\n"
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if flag==0:
                    prev_tripID=row["trip_id"]
                    flag=1
                if prev_tripID!=row["trip_id"] and trip_dict[prev_tripID]!=trip_dict[row["trip_id"]]:
                    route_ordered_dict[trip_dict[row["trip_id"]]].append(temp)
                    temp=[]
                    flag=0
                if prev_tripID!=row["trip_id"]:
                    temp=[]
                temp.append(row["stop_id"])
                prev_tripID=row["trip_id"]
        routes_data = trips.readCSV(self.trip_files[3])
        print "The list of Routes and their stops in order are:\n"
        for row in routes_data:
            print "Route: ", row["route_id"],"\tStops: ",route_ordered_dict[row["route_id"]]
        adja_M = self.update_weights(adja_M, route_dict, route_keys, trip_dict, stop_index_dict, content_transfer_time)
        self.start_transfer(stop_freq[0][0], content_transfer_time, route_keys, adja_M)
        return trajectories

    def update_weights(self, adja_M, route_dict, route_keys, trip_dict, stop_index_dict, content_transfer_time):
        trips = parseGTFS(self.trip_files)
        routes_data = trips.readCSV(self.trip_files[3])
        stop_times = parseGTFS(trip_files)
        start_t=0
        """for row in routes_data:
            for j in range(len(route_dict[row["route_id"]])-1):
                flag=0
                stop_times_data = stop_times.readCSV(self.trip_files[5])
                for rows in stop_times_data:
                    if self.toElapsedTime(rows["departure_time"])>=self.toElapsedTime(content_transfer_time):
                        if trip_dict[rows["trip_id"]]==row["route_id"] and route_dict[row["route_id"]][j]==rows["stop_id"] and flag==0:
                            current_trip=rows["trip_id"]
                            start_t=self.toElapsedTime(rows["departure_time"])
                            flag=1
                        elif flag==1 and current_trip==rows["trip_id"] and trip_dict[rows["trip_id"]]==row["route_id"] and route_dict[row["route_id"]][j+1]==rows["stop_id"]:
                            adja_M[stop_index_dict[route_dict[row["route_id"]][j]]][stop_index_dict[route_dict[row["route_id"]][j+1]]]= start_t - self.toElapsedTime(rows["departure_time"])
                            #print adja_M[stop_index_dict[route_dict[row["route_id"]][j]]][stop_index_dict[route_dict[row["route_id"]][j+1]]]
                            break
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                if adja_M[i][j]>0:
                    print adja_M[i][j]"""
        return adja_M

    def start_transfer(self, stop_id, content_transfer_time, route_keys, adja_M):
        #adjmatrix= [[0 for x in range(len(route_keys))]for x in range(len(route_keys))]
        Arc = namedtuple('Arc', ('tail', 'weight', 'head'))
        start=route_keys.index(stop_id)
        list_arcs=[]
        #print adja_M
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                if adja_M[i][j]!=0:
                    list_arcs.append(Arc(j, adja_M[i][j], i))
        #print self.min_spanning_arborescence(list_arcs, 0)

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

trip_files = ["../MUNI/agency.txt", "../MUNI/calendar_dates.txt", "../MUNI/calendar.txt", "../MUNI/routes.txt", "../MUNI/shapes.txt", "../MUNI/stop_times.txt", "../MUNI/stops.txt", "../MUNI/transfers.txt", "../MUNI/trips_1.txt"]
inst = parseGTFS(trip_files)
inst_data = inst.parseTrips("monday", "08:00:00")
