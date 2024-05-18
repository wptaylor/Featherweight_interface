import serial, csv, os
import datetime

packet_headers, header_files = [], []


## SET BASED ON USB PLUG / TRACKER IN-USE ##
SERIAL_PORT_NUMBER = 6


def main():
    serialPort = start_serial(SERIAL_PORT_NUMBER)
    (starting_date_string, starting_time_string) = start_datetime()
    navigate_datetime_directory(starting_date_string, starting_time_string)

    bufferstring = ""

    while 1:
        if serialPort.in_waiting > 0:
            serialString = serialPort.read()
            newchar = serialString.decode("ascii", errors="ignore")
            bufferstring += newchar
            if newchar == "\n":
                bufferstring = bufferstring.replace("\r", "")
                if not (
                    len(bufferstring) == 1
                    or "FWT" in bufferstring
                    or "!FWADR" in bufferstring
                ):
                    bufferstring = bufferstring[:-1]
                    parse_message(bufferstring)
                bufferstring = ""


def start_serial(port_num: int):
    serialPort = serial.Serial(
        port="COM%d" % port_num,
        baudrate=115200,
        bytesize=8,
        timeout=2,
        stopbits=serial.STOPBITS_ONE,
    )
    return serialPort


def start_datetime():
    starting_datetime = datetime.datetime.now()
    starting_date_string = starting_datetime.strftime("%Y-%m-%d")
    starting_time_string = starting_datetime.strftime("%H%M%S")
    return (starting_date_string, starting_time_string)


def navigate_datetime_directory(starting_date_string, starting_time_string):
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    os.chdir("logs")
    if not os.path.isdir(starting_date_string):
        os.mkdir(starting_date_string)
    os.chdir(starting_date_string)
    os.mkdir(starting_time_string)
    os.chdir(starting_time_string)


def split_message(message: str) -> list:
    message_split_list = message.split(" ")
    message_split_list = [split for split in message_split_list if len(split) > 0]
    message_split_list = message_split_list[:-1]
    return message_split_list


def parse_message(message: str):
    message_split = split_message(message)
    if len(message_split) < 1 or not message_split[0] == "@":
        return
    header = message_split[1]
    if header not in packet_headers:
        packet_headers.append(header)
        with open("%s.csv" % header, "w") as f:
            pass
    with open("%s.csv" % header, "a") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(message_split)
        if message_split[1] == "GPS_STAT":
            parse_gps_to_csv(message)
            print_gps_terminal(message)

    

def parse_gps_to_csv(message: str):
    message_split = split_message(message)
    if (len(message_split) < 1) or not message_split[0] == "@":
        return
    
    if (message_split[1] != "GPS_STAT"):
        return

    if "VISUALIZER_DATA" not in packet_headers:
        packet_headers.append("VISUALIZER_DATA")
        with open("VISUALIZER_DATA.csv", "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["Altitude (ft)", "Latitude", "Longitude", "Date (YYYY-MM-DD)", "Time"])
    
    with open("VISUALIZER_DATA.csv", "a") as f:
        writer = csv.writer(f, delimiter=",")
        loggingdatetime = datetime.datetime.now()
        writer.writerow([message_split[11], 
                         message_split[13], 
                         message_split[15],
                         loggingdatetime.strftime("%Y-%m-%d"),
                         message_split[6]
                        ]
                    )

def print_gps_terminal(message:str):
    message_split = split_message(message)
    if len(message_split) < 1 or not message_split[0] == "@":
        return
    if message_split[1] == "GPS_STAT":
        print(
            message_split[8],
            message_split[9],
            message_split[11],
            message_split[13],
            message_split[15],
            message_split[17],
            message_split[19],
            )



if __name__ == "__main__":
    main()
