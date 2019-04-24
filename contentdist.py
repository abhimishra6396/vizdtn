import csv
import geopy.distance
from shapely.geometry import LineString, Point
import time
import operator
from collections import defaultdict, namedtuple
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from graph_tool.all import *

class GraphMST:
    def __init__(self,vertices):
        self.V= vertices #No. of vertices
        self.graph = [] #default dictionary

    def addEdge(self,u,v,w):
        self.graph.append([u,v,w])

    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)

        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot

        else :
            parent[yroot] = xroot
            rank[xroot] += 1

    def KruskalMST(self):

        result =[] #This will store the resultant MST

        i = 0 # An index variable, used for sorted edges
        e = 0 # An index variable, used for result[]

        self.graph =  sorted(self.graph,key=lambda item: item[2])

        parent = [] ; rank = []

        # Create V subsets with single elements
        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        # Number of edges to be taken is equal to V-1
        while e < self.V -1 :

            u,v,w =  self.graph[i]
            i = i + 1
            x = self.find(parent, u)
            y = self.find(parent ,v)

            if x != y:
                e = e + 1
                result.append([u,v,w])
                self.union(parent, rank, x, y)

        print ("Following are the edges in the constructed MST")
        """for u,v,weight  in result:
            #print str(u) + " -- " + str(v) + " == " + str(weight)
            print ("%d -- %d == %d" % (u,v,weight))"""
        return result

class GraphDirected:
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

class parseGTFS(GraphDirected, GraphMST):
    def __init__(self,trip_files):
        self.trip_files = trip_files
        self.visited_count = 0
        self.visited_stops_set=set()
        self.stop_data_received_time = {}
        self.stop_first_received_time = {}
        self.flooding_progress=[]
        self.route_count=0
        self.route_check={}
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
        trip_direction={} #trip_id to direction_id mapping
        route_dict={} #route id to all it's contained multi route stops
        route_ordered_dict={} #route id to it's stops in order
        trip_service_dict={} #trip id to bool suggesting if that trip was present
        stop_trip_dict={} #stop_id to list of available trips after content_transfer_time
        trip_length_dict={} #trip_id to its length mapping
        route_maxlen_trip={} #route_id to trip with max length
        wkd=0
        i=0
        flag=0
        if day in ["monday","tuesday","wednesday","thursday","friday"]:
            wkd=1
        for row in trips_data:
            trip_dict[row["trip_id"]]=row["route_id"]
            trip_direction[row["trip_id"]]=int(row["direction_id"])
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
        print ("Number of Trips this day is: %d\n" %len(trip_set))
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[6])
        for row in stops_data:
            stop_trip_dict[row["stop_id"]] = []
            stop_dict[row["stop_id"]] = [row["stop_lat"],row["stop_lon"],0,0,set()]
        print ("Number of Stops in this transport system is: %d\n" %len(stop_dict))
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                trip_length_dict[row["trip_id"]]=0
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        flag=0
        prev_trip=0
        trip_length=1
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if flag==0:
                    prev_trip=row["trip_id"]
                    flag=1
                else:
                    if row["trip_id"]==prev_trip:
                        trip_length+=1
                    else:
                        trip_length_dict[prev_trip]=trip_length
                        trip_length=1
                        prev_trip=row["trip_id"]
                if (self.toElapsedTime(row["departure_time"])>self.toElapsedTime(content_transfer_time)):
                    stop_trip_dict[row["stop_id"]].append((row["trip_id"], self.toElapsedTime(row["departure_time"])))
                if int(row["stop_sequence"])==1:
                    stop_dict[row["stop_id"]][2]+=1
        for key in stop_trip_dict.keys():
            stop_trip_dict[key]=sorted(stop_trip_dict[key], key=itemgetter(1))
        stop_freq = sorted(stop_dict.items(), key=lambda x: x[1][2], reverse=True)
        print ("Most Frequent stop for trip to start is: %d which is visited %d times.\n" %(int(stop_freq[0][0]), int(stop_freq[0][1][2])))
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
        print ("\n\n\n\n\n\n\n\n\n\n")
        print ("Stops with multiple routes are:\n")
        i=0
        for key in stop_dict.keys():
            if stop_dict[key][3]==1:
                print ("Stop ID: ",key,"\tRoutes: ", list(stop_dict[key][4]))
                route_keys.append(key)
                stop_index_dict[key] = i
                i+=1
                count+=1
        print ("There are %d Stops that have multiple routes" %count)
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        adja_M = [[100000 for x in range(len(route_keys))]for x in range(len(route_keys))]
        """for i in range(len(route_keys)):
            ind_array.append(stop_index_dict[route_keys[i]])
        for i in range(len(stop_dict)):
            for j in range(len(stop_dict)):
                if ~(i in ind_array):
                    adja_M[i][j]=0"""
        routes = parseGTFS(trip_files)
        routes_data = trips.readCSV(self.trip_files[3])
        for row in routes_data:
            route_maxlen_trip[row["route_id"]+"u"]=0
            route_maxlen_trip[row["route_id"]+"d"]=0
            path_dict={}
            for i in range(140):
                path_dict[i+1]=[set(),set(),0,0] #direction_id 0,direction_id 1, time taken from prev. stop in direction_id 0, time taken from prev. stop in direction_id 1
            route_dict[row["route_id"]]=[]
            route_ordered_dict[row["route_id"]]=path_dict
            for keys in route_keys:
                self.stop_data_received_time[keys]=self.toElapsedTime(content_transfer_time)
                self.stop_first_received_time[keys]=self.toElapsedTime(content_transfer_time)
                if row["route_id"] in list(stop_dict[keys][4]):
                    route_dict[row["route_id"]].append(keys)
        routes_data = trips.readCSV(self.trip_files[3])
        print ("\n\n\n\n\n\n\n\n\n\n")
        print ("The list of Routes and their multi-route stops are:\n")
        for row in routes_data:
            print (("Route: "), row["route_id"], ("\tStops: "), route_dict[row["route_id"]])
        flag=0
        print ("\n\n\n\n\n\n\n\n\n\n")
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if route_maxlen_trip[trip_dict[row["trip_id"]]+"u"]!=0 and trip_direction[row["trip_id"]]==0:
                    if route_maxlen_trip[trip_dict[row["trip_id"]]+"u"][1] < trip_length_dict[row["trip_id"]]:
                        route_maxlen_trip[trip_dict[row["trip_id"]]+"u"] = (row["trip_id"], trip_length_dict[row["trip_id"]])
                elif route_maxlen_trip[trip_dict[row["trip_id"]]+"d"]!=0 and trip_direction[row["trip_id"]]==1:
                    if route_maxlen_trip[trip_dict[row["trip_id"]]+"d"][1] < trip_length_dict[row["trip_id"]]:
                        route_maxlen_trip[trip_dict[row["trip_id"]]+"d"] = (row["trip_id"], trip_length_dict[row["trip_id"]])
                else:
                    if trip_direction[row["trip_id"]]==0:
                        route_maxlen_trip[trip_dict[row["trip_id"]]+"u"] = (row["trip_id"], trip_length_dict[row["trip_id"]])
                    elif trip_direction[row["trip_id"]]==1:
                        route_maxlen_trip[trip_dict[row["trip_id"]]+"d"] = (row["trip_id"], trip_length_dict[row["trip_id"]])
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for row in stop_times_data:
            if trip_service_dict[row["trip_id"]]==1:
                if trip_direction[row["trip_id"]]==0:
                    if route_maxlen_trip[trip_dict[row["trip_id"]]+"u"][0]==row["trip_id"]:
                        route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][0].add(row["stop_id"])
                        if route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][2]==0:
                            route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][2]=self.toElapsedTime(row["departure_time"])
                else:
                    if route_maxlen_trip[trip_dict[row["trip_id"]]+"d"][0]==row["trip_id"]:
                        route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][1].add(row["stop_id"])
                        if route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][3]==0:
                            route_ordered_dict[trip_dict[row["trip_id"]]][int(row["stop_sequence"])][3]=self.toElapsedTime(row["departure_time"])
        routes_data = trips.readCSV(self.trip_files[3])
        print ("The list of Routes and their stops in order are:\n")
        for row in routes_data:
            print (("Route: "), row["route_id"], ("\tStops: "), route_ordered_dict[row["route_id"]], ("\n\n\n"))
        adja_M = self.update_weights(adja_M, route_dict, route_keys, trip_dict, stop_index_dict, route_ordered_dict, content_transfer_time, stop_dict)
        self.start_transfer_dijkstra(stop_freq[0][0], content_transfer_time, route_keys, adja_M)
        source_stop="4073"
        #self.drawGraphs(source_stop, content_transfer_time, route_keys, adja_M)
        #self.flooding(adja_M, route_dict, route_keys, trip_dict, route_ordered_dict, content_transfer_time, trip_service_dict, source_stop, stop_dict, stop_trip_dict, stop_index_dict, trip_direction)
        #self.plot_flooding(source_stop, stop_dict, route_keys, content_transfer_time)
        #print trip_length_dict["8511736"]
        #print route_maxlen_trip
        #print stop_trip_dict
        return trajectories

    def update_weights(self, adja_M, route_dict, route_keys, trip_dict, stop_index_dict, route_ordered_dict, content_transfer_time, stop_dict):
        trips = parseGTFS(self.trip_files)
        stop_times = parseGTFS(trip_files)
        start_t=0
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        for keys in route_ordered_dict.keys():
            flag1=0
            flag2=0
            for i in range(140):
                if len(route_ordered_dict[keys][i+1][0])>0:
                    if flag1==0 and stop_dict[list(route_ordered_dict[keys][i+1][0])[0]][3]==1:
                        prev_up=list(route_ordered_dict[keys][i+1][0])[0]
                        prev_weight_up=route_ordered_dict[keys][i+1][2]
                        flag1=1
                    else:
                        if stop_dict[list(route_ordered_dict[keys][i+1][0])[0]][3]==1:
                            adja_M[stop_index_dict[prev_up]][stop_index_dict[list(route_ordered_dict[keys][i+1][0])[0]]]=route_ordered_dict[keys][i+1][2]-prev_weight_up
                            prev_up=list(route_ordered_dict[keys][i+1][0])[0]
                            prev_weight_up=route_ordered_dict[keys][i+1][2]
                if len(route_ordered_dict[keys][i+1][1])>0:
                    if flag2==0 and stop_dict[list(route_ordered_dict[keys][i+1][1])[0]][3]==1:
                        prev_down=list(route_ordered_dict[keys][i+1][1])[0]
                        prev_weight_down=route_ordered_dict[keys][i+1][3]
                        flag2=1
                    else:
                        if stop_dict[list(route_ordered_dict[keys][i+1][1])[0]][3]==1:
                            adja_M[stop_index_dict[prev_down]][stop_index_dict[list(route_ordered_dict[keys][i+1][1])[0]]]=route_ordered_dict[keys][i+1][3]-prev_weight_down
                            prev_down=list(route_ordered_dict[keys][i+1][1])[0]
                            prev_weight_down=route_ordered_dict[keys][i+1][3]
        """for i in range(len(adja_M[0])):
            for j in range(len(adja_M[0])):
                if adja_M[i][j]>0:
                    print adja_M[i][j]
            print "\n"""
        return adja_M

    def start_transfer_edmond(self, stop_id, content_transfer_time, route_keys, adja_M):
        #adjmatrix= [[0 for x in range(len(route_keys))]for x in range(len(route_keys))]
        Arc = namedtuple('Arc', ('tail', 'weight', 'head'))
        start=route_keys.index(stop_id)
        list_arcs=[]
        #print adja_M
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                #if adja_M[i][j]>0:
                list_arcs.append(Arc(j, adja_M[i][j], i))
        print (self.min_spanning_arborescence(list_arcs, start))

    def start_transfer_dijkstra(self, stop_id, content_transfer_time, route_keys, adja_M):
        start=route_keys.index(stop_id)
        g=GraphMST(len(route_keys))
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                    g.addEdge(i, j, adja_M[i][j])
        val=g.KruskalMST()
        print (val)
        adja_spanning=[[100000 for x in range(len(route_keys))]for x in range(len(route_keys))]
        for i in range(len(val)):
            adja_spanning[val[i][0]][val[i][1]]=val[i][2]
        self.drawGraphs(stop_id, content_transfer_time, route_keys, adja_spanning)

    def flooding(self, adja_M, route_dict, route_keys, trip_dict, route_ordered_dict, content_transfer_time, trip_service_dict, stop_id, stop_dict, stop_trip_dict, stop_index_dict, trip_direction):
        trips = parseGTFS(self.trip_files)
        stop_times = parseGTFS(trip_files)
        start_t=0
        stop_times_data = stop_times.readCSV(self.trip_files[5])
        trip_timed=[]
        for rows in stop_times_data:
            if int(rows["stop_sequence"])==1 and trip_service_dict[rows["trip_id"]]==1:
                trip_timed.append((rows["trip_id"],self.toElapsedTime(rows["departure_time"])))
        trip_timed=sorted(trip_timed, key=itemgetter(1))
        content_transfer_time=self.toElapsedTime(content_transfer_time)
        tot_trips=len(trip_timed)
        val=0
        for i in range(tot_trips):
            if trip_timed[i][1]>content_transfer_time:
                if trip_dict[trip_timed[i][0]] in stop_dict[stop_id][4]:
                    val=i
                    #self.recTransfer(route_dict, route_keys, trip_dict, route_ordered_dict, content_transfer_time, trip_service_dict, stop_id, stop_dict, trip_timed, i, "4381")
                    break
        for keys in route_dict.keys():
            self.route_check[keys+"u"]=0
            self.route_check[keys+"d"]=0
        flag=0
        next_mult=set()
        current_mult=set()
        #while self.route_count <= len(self.route_check.keys())-20:
        self.flooding_progress.append((0, 0))
        while self.visited_count < 10000:
            if flag==0 and len(next_mult)==0:
                for items in stop_dict[stop_id][4]:
                    current_mult.update(route_dict[items])
                    self.route_check[items+"u"]=1
                    self.route_check[items+"d"]=1
                flag=1
            elif flag==0 and len(next_mult)>0:
                current_mult=next_mult
                next_mult=set()
            for items in current_mult:
                    next_mult.update(self.recTransfer(adja_M, route_dict, route_keys, trip_dict, route_ordered_dict, content_transfer_time, trip_service_dict, items, stop_dict, trip_timed, val, stop_trip_dict, stop_index_dict, trip_direction))
            flag=0
            val+=1
            if len(self.visited_stops_set)>=len(route_keys):
                break
            temp=0
            for key in self.route_check.keys():
                if self.route_check[key]==1:
                    temp+=1
            self.route_count=temp
            #if sum(value == 1 for value in self.route_check.values())>=2*len(route_dict.keys()):
            #    break
            #print len(current_mult)
            self.flooding_progress.append((len(current_mult), max(self.stop_data_received_time.values())-content_transfer_time))

        print (self.visited_count, len(self.visited_stops_set), len(route_keys))

    def recTransfer(self, adja_M, route_dict, route_keys, trip_dict, route_ordered_dict, content_transfer_time, trip_service_dict, stop_id, stop_dict, trip_timed, i, stop_trip_dict, stop_index_dict, trip_direction):
        self.visited_count+=1
        self.visited_stops_set.add(stop_id)
        temp=set()
        temp_stop_route={}
        for items in stop_dict[stop_id][4]:
            temp.update(route_dict[items])
            self.route_check[items+"u"]=1
            self.route_check[items+"d"]=1
            temp_stop_route[items+"u"]=0
            temp_stop_route[items+"d"]=0
        j=0
        k=0
        while j<len(temp_stop_route) and k<len(stop_trip_dict[stop_id]):
            if stop_trip_dict[stop_id][k][1] > self.stop_data_received_time[stop_id]:
                if temp_stop_route[trip_dict[stop_trip_dict[stop_id][k][0]]+"u"]==0 and trip_direction[stop_trip_dict[stop_id][k][0]]==0:
                    temp_stop_route[trip_dict[stop_trip_dict[stop_id][k][0]]+"u"]=1
                    source_seq=0
                    dest_seq=0
                    for i in range(140):
                        if len(list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][0]))>0:
                            if list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][0])[0]==stop_id:
                                source_seq=i+1
                                break
                    for items in route_dict[trip_dict[stop_trip_dict[stop_id][k][0]]]:
                        for i in range(140):
                            if len(list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][0]))>0:
                                if list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][0])[0]==items:
                                    dest_seq=i+1
                                    break
                        if dest_seq > source_seq:
                            if self.stop_data_received_time[items]!=content_transfer_time:
                                self.stop_data_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                            else:
                                self.stop_data_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                                self.stop_first_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                    j+=1
                elif temp_stop_route[trip_dict[stop_trip_dict[stop_id][k][0]]+"d"]==0 and trip_direction[stop_trip_dict[stop_id][k][0]]==1:
                    temp_stop_route[trip_dict[stop_trip_dict[stop_id][k][0]]+"d"]=1
                    source_seq=0
                    dest_seq=0
                    for i in range(140):
                        if len(list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][1]))>0:
                            if list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][1])[0]==stop_id:
                                source_seq=i+1
                                break
                    for items in route_dict[trip_dict[stop_trip_dict[stop_id][k][0]]]:
                        for i in range(140):
                            if len(list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][1]))>0:
                                if list(route_ordered_dict[trip_dict[stop_trip_dict[stop_id][k][0]]][i+1][1])[0]==items:
                                    dest_seq=i+1
                                    break
                        if dest_seq > source_seq:
                            if self.stop_data_received_time[items]!=content_transfer_time:
                                self.stop_data_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                            else:
                                self.stop_data_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                                self.stop_first_received_time[items]=self.stop_data_received_time[stop_id]+adja_M[stop_index_dict[stop_id]][stop_index_dict[items]]
                    j+=1
            k+=1
        return temp

        #print trip_timed, content_transfer_time

    def plot_flooding(self, source_stop, stop_dict, route_keys, content_transfer_time):
        dist_source=[]
        for keys in route_keys:
            dist_source.append((keys, abs(geopy.distance.geodesic((stop_dict[source_stop][0], stop_dict[source_stop][1]), (stop_dict[keys][0], stop_dict[keys][1])).km), self.stop_first_received_time[keys]-self.toElapsedTime(content_transfer_time)))
        dist_source=sorted(dist_source, key=itemgetter(1))
        plt.figure(1)
        plt.plot([item[2] for item in dist_source])
        plt.title("time_taken_flooding_distance_from_source")
        plt.xlabel('stops sorted on distance')
        plt.ylabel('time taken in seconds')
        plt.savefig('time_taken_flooding_distance_from_source.png')
        plt.figure(2)
        plt.plot([item[0] for item in self.flooding_progress], [item[1] for item in self.flooding_progress])
        plt.title("flooding_progress_with_time")
        plt.xlabel('number of stops')
        plt.ylabel('time in seconds')
        plt.savefig('flooding_progress_with_time.png')
        #print dist_source
        print (self.flooding_progress)

    def drawGraphs(self, stop_id, content_transfer_time, route_keys, adja_M):
        g=Graph()
        v=[]
        e=[]
        v_prop = g.new_vertex_property("string")
        #e_prop = g.new_edge_property("string")
        e_len = g.new_edge_property("int")
        for i in range(len(route_keys)):
            v.append(g.add_vertex())
            v_prop[v[i]] = route_keys[i]
        for i in range(len(adja_M)):
            for j in range(len(adja_M)):
                if adja_M[i][j]<100000:
                    e.append(g.add_edge(v[i], v[j]))
                    e_len[e[len(e)-1]] = adja_M[i][j]

        graph_draw(g, vertex_text=v_prop, edge_text = e_len, edge_pen_width = 1, vertex_size=10, vertex_font_size=8, output_size=(6000, 6000), output="Spanning_Tree.png")

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
source_stops = ["7620", "4073", "5462", "6835", "6050", "7329", "5836", "6415", "4110", "5427"]
inst = parseGTFS(trip_files)
inst_data = inst.parseTrips("monday", "08:00:00")
#plt.plot(source_stops, [1325,1990,2104,1297,1529,1825,1492,2332,1852,2004])
#plt.title("Flooding")
#plt.xlabel('Source Stop')
#plt.ylabel('Number of Copies')
#plt.show()
