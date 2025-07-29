# n1mm2adif_server
 UDP QSO Logger for N1MM Logger+

This Python script acts as a lightweight UDP server designed to integrate with N1MM Logger+. 
It listens for XML-based <contactinfo> packets sent over UDP when a QSO is logged and appends a line of ADIF to a log file.
This file can be monitored by a logging program (in my case VQLog) in the same way as WSJTX log files are monitored, so that 
appended entries are added to the station log.

## What It Does:
    Listens on UDP port 12060 for incoming <contactinfo> XML packets.
    Parses and extracts key QSO details from each packet (e.g., callsign, frequency, mode, signal reports, timestamp).
    Converts and formats the data into a structured tag-based text format.
    Appends each QSO as a single line to an adif log file at:
    C:\Users\neil\Documents\N1MM Logger+\ExportFiles\auto_adi
    Automatically starts with N1MM Logger+ via an AutoHotKey launch script.

## Notes:
    Frequency is interpreted from txfreq, assuming units of 10 Hz.
    Band is inferred from frequency using typical amateur radio band ranges.
    The script runs continuously and logs each valid <contactinfo> packet in real time.
    
## Requirements
    AutoHotKey must be installed if automatic launch on N1MM startup is required
    
 
