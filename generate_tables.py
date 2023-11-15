def _append_point_table(pl_id, fk, table, point, lon, lat):
    coords = (lon, lat)
    point.properties = {"id": pl_id, "fk": fk} | point.properties
    table.append((coords, point.properties))

def places(places):
    # ( (lon, lat), properties )
    place_visits = []
    place_visits_children = []
    place_visits_other_candidate_locations = []
    place_visits_children_other_candidate_locations = []
    
    # ( lon, lat), properties )
    place_visit_points = []
    
    place_visits_id = 0
    place_visits_children_id = 0
    place_visits_other_candidate_locations_id = 0
    place_visits_children_other_candidate_locations_id = 0
    
    place_visit_points_id = 0
    
    for place in places:
        place[0].properties = {"id": place_visits_id} | place[0].properties
        place_coords = (place[0].lon, place[0].lat)
        place_visits.append((place_coords, place[0].properties))
        
        for candidate in place[0].otherCandidateLocations:
            _append_point_table(
                place_visits_other_candidate_locations_id, 
                place_visits_id, 
                place_visits_other_candidate_locations, 
                candidate, 
                candidate.properties.pop("location_lon"), 
                candidate.properties.pop("location_lat")
            )
            place_visits_other_candidate_locations_id += 1
        for child in place[0].children:
            _append_point_table(place_visits_children_id, place_visits_id, place_visits_children, child, child.lon, child.lat)
            for child_candidate in child.otherCandidateLocations:
                _append_point_table(
                    place_visits_children_other_candidate_locations_id, 
                    place_visits_children_id, 
                    place_visits_children_other_candidate_locations, 
                    child_candidate, 
                    child_candidate.properties.pop("location_lon"),
                    child_candidate.properties.pop("location_lat")
                )
                place_visits_children_other_candidate_locations_id += 1
            place_visits_children_id += 1
        
        for record in place[1]:
            _append_point_table(place_visit_points_id, place_visits_id, place_visit_points, record, record.lon, record.lat)
            place_visit_points_id += 1
            
        place_visits_id += 1
    return (place_visits, place_visits_children, place_visits_other_candidate_locations, place_visits_children_other_candidate_locations, place_visit_points)
    
# ( (coords[], properties), (coords, properties), (coords[], properties), (coords, properties) )
# (activities, activity points, transit paths, transit points) 
def activities(activities):
    activity_segments = []
    activity_points = []
    
    transit_paths = []
    transit_points = []
    
    activity_segment_id = 0
    activity_point_id = 0
    transit_path_id = 0
    transit_point_id = 0
    
    for activity in activities:
        activity[0].properties = {"id": activity_segment_id} | activity[0].properties
        activity_coords = list(map(lambda record: (record.lon, record.lat), activity[1]))
        activity_segments.append((activity_coords, activity[0].properties))
        for record in activity[1]:
            _append_point_table(activity_point_id, activity_segment_id, activity_points, record, record.lon, record.lat)
            activity_point_id += 1
        
        if activity[0].transit_path is not None:
            path = activity[0].transit_path
            path.properties = {"id": transit_path_id, "fk": activity_segment_id} | path.properties
            transit_path_coords = list(map(lambda stop: (stop.lon, stop.lat), path.stops))
            transit_paths.append((transit_path_coords, path.properties))
            for stop in path.stops:
                _append_point_table(transit_point_id, transit_path_id, transit_points, stop, stop.lon, stop.lat)
                transit_point_id += 1
            transit_path_id += 1
        activity_segment_id += 1
    return (activity_segments, activity_points, transit_paths, transit_points)