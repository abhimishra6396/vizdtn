import csv
import geopy

class parseGTFS:
    def __init__(self,trip_files):
        self.trip_files = trip_files
    def readCSV(self, file_name):
        csv_file = open(file_name, mode='r')
        data = csv.DictReader(csv_file)
        return data
    def parseTrips(self):
        trips = parseGTFS(trip_files)
        trips_data = trips.readCSV(self.trip_files[7])
        line_count=0
        trip_set=set()
        trajectories=[]
        stop_dict={}
        for row in trips_data:
            prev_len=len(trip_set)
            trip_set.add(row["trip_id"])
            new_len=len(trip_set)
            if (prev_len!=new_len):
                trajectories.append(Trajectory(row["trip_id"], row["service_id"]))
        stops = parseGTFS(trip_files)
        stops_data = stops.readCSV(self.trip_files[5])
        for row in stops_data:
            stop_dict[row["stop_id"]] = (row["stop_lat"],row["stop_lon"])
        stop_times = parseGTFS(trip_files)
        stop_times_data = stop_times.readCSV(self.trip_files[4])
        return trajectories

class Trajectory:
    def __init__(self,trip_id,service_id):
        self.trip_id=trip_id
        self.service_id=service_id
        self.trajectory=[]
    def getPosition(time):
        return coordinate
    def isActive(time):
        return isvActive

class Transit:
    def __init__(self,file_name,trajectories):
        self.file_name=file_name
        self.trajectories=trajectories
    def activeTrajectories(time):
        return allActiveTrajectories

trip_files = ["RATP_GTFS_FULL/agency.txt", "RATP_GTFS_FULL/calendar_dates.txt", "RATP_GTFS_FULL/calendar.txt", "RATP_GTFS_FULL/routes.txt", "RATP_GTFS_FULL/stop_times.txt", "RATP_GTFS_FULL/stops.txt", "RATP_GTFS_FULL/transfers.txt", "RATP_GTFS_FULL/trips.txt"]
inst = parseGTFS(trip_files)
inst_data = inst.parseTrips()
