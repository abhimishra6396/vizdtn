import csv
import geopy.distance
from shapely.geometry import LineString, Point
import time
import operator
from collections import defaultdict, namedtuple

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
    def toElapsedTime(self, date_time, current_date):
        time_midnight = 3600*int(date_time[0]) + 60*int(date_time[1]) + int(date_time[2])
        return time_midnight
    def parseTrips(self, day, content_transfer_time):
        calendar = parseGTFS(trip_files)
        calendar_data = calendar.readCSV(self.trip_files[2])
        trips = parseGTFS(trip_files)
        trips_data = trips.readCSV(self.trip_files[8])
        trip_set=set()
        trajectories=[]
        stop_dict={}
        trip_dict={}
        route_dict={}
        wkd=0
        if day in ["monday","tuesday","wednesday","thursday","friday"]:
            wkd=1
        for row in trips_data:
            trip_dict[row["trip_id"]]=row["route_id"]
            if wkd==1:
                if row["service_id"]=="1":
                    prev_len=len(trip_set)
                    trip_set.add(row["trip_id"])
                    if (prev_len!=len(trip_set)):
                        trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
            else:
                if day=="saturday":
                    if row["service_id"]=="2":
                        prev_len=len(trip_set)
                        trip_set.add(row["trip_id"])
                        if (prev_len!=len(trip_set)):
                            trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
                else:
                    if row["service_id"]=="3":
                        prev_len=len(trip_set)
                        trip_set.add(row["trip_id"])
                        if (prev_len!=len(trip_set)):
                            trajectories.append(Trajectory(row["trip_id"], row["service_id"], row["shape_id"]))
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[6])
        for row in stops_data:
            stop_dict[row["stop_id"]] = [row["stop_lat"],row["stop_lon"],0,0,set()]
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if int(row["stop_sequence"])==1:
                stop_dict[row["stop_id"]][2]+=1
        stop_freq = sorted(stop_dict.items(), key=lambda x: x[1][2], reverse=True)
        #print stop_freq[0]
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        count=0
        for row in stop_times_data:
            if len(stop_dict[row["stop_id"]][4])==0:
                    stop_dict[row["stop_id"]][4].add((trip_dict[row["trip_id"]], row["stop_sequence"]))
            elif ~(trip_dict[row["trip_id"]] in stop_dict[row["stop_id"]][4]):
                    stop_dict[row["stop_id"]][4].add((trip_dict[row["trip_id"]], row["stop_sequence"]))
            if len(stop_dict[row["stop_id"]][4])>1:
                stop_dict[row["stop_id"]][3]=1
        route_keys=[]
        for key in stop_dict.keys():
            if stop_dict[key][3]==1:
                route_keys.append(key)
        #print stop_dict["7620"]
        routes = parseGTFS(trip_files)
        routes_data = trips.readCSV(self.trip_files[3])
        for row in routes_data:
            route_dict[row["route_id"]]=[[]]
            for keys in route_keys:
                for id, val in enumerate(stop_dict[keys][4]):
                    if row["route_id"]==val[0]:
                        route_dict[row["route_id"]][0].append([keys,val[1]])
        routes_data = trips.readCSV(self.trip_files[3])
        for row in routes_data:
            count_route = [0 for x in range(200)]
            for i in range(len(route_dict[row["route_id"]][0])):
                for j in route_dict[row["route_id"]][0]:
                    if int(j[1])==i:
                        count_route[i]+=1
            #print row["route_id"], route_dict[row["route_id"]][0], count_route
        adja_M = [[0 for x in range(len(route_keys))]for x in range(len(route_keys))]
        routes_data = trips.readCSV(self.trip_files[3])
        for row in routes_data:
            route_dict[row["route_id"]][0].sort(key=lambda l:int(l[1]))
            for j in range(len(route_dict[row["route_id"]][0])-1):
                adja_M[route_keys.index(route_dict[row["route_id"]][0][j][0])][route_keys.index(route_dict[row["route_id"]][0][j+1][0])]=1
        self.start_transfer(stop_freq[0][0], content_transfer_time, route_keys, adja_M)
        return trajectories

    def start_transfer(self, stop_id, content_transfer_time, route_keys, adja_M):
        #adjmatrix= [[0 for x in range(len(route_keys))]for x in range(len(route_keys))]
        Arc = namedtuple('Arc', ('tail', 'weight', 'head'))
        start=route_keys.index(stop_id)
        list_arcs=[]
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                #if adja_M[i][j]>0:
                list_arcs.append(Arc(j, adja_M[i][j], i))
        print self.min_spanning_arborescence(list_arcs, 0)

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
inst_data = inst.parseTrips("monday", 3600*9)
