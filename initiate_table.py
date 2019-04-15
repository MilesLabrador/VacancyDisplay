import pandas as pd
apartment_information = pd.DataFrame(columns=['room_id', 'room_type', 'available_spaces', 'apt_building', 'floor', 'suite_id', 'bed_spaces', 'timestamp'])
apartment_information.to_csv('apartment_availability.csv', index=False)
