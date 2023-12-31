def clean_pinecone(response):
    #Dict for metadata that is removed from duplicate classes
    additional_metadata = {}
    classes = [] 
    unique_codes = set()

    for entry in response['matches']:
        code = entry['metadata']['code']
        score = float(entry['score'])
        # score = 
        if score > 0.785: #Threshold from personal testing
            if code not in unique_codes:
                #Where class is unique
                classes.append(entry)
                unique_codes.add(code)
            else:
                #Class already added, but need to save alternate sessions
                time = entry['metadata']['time']
                days = entry['metadata']['days']
                additional_metadata[code] = {'time': time, 'days': days}

    return classes, additional_metadata

def build_filter(json_response):
    filter = {}

    days_list = json_response['Days']
    # Days
    if "[" in days_list:
        days = str(days_list[0])

        for i in range(len(days_list)-1):
            days += ', '
            days += str(days_list[i+1])
        filter["days"] = days

    # Units
    units = json_response['Units']

    if units != "":
        filter["units"] = units

    # Program
    program = json_response['Program']

    if program != "":
        filter["program"] = program

    # Time

    return filter
