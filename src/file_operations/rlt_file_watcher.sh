#!/bin/ksh

# Script to watch for new data files in the data directory
# and trigger the data processing and loading script

if [ $# -ne 2 ]; then
    echo "Usage: ./rlt_file_watcher.sh <start|stop> <data_directory>"
    exit 1
fi

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

check_and_create_directories() {

    if [ ! -d "$data_dir/processed" ]; then
        log_message "Creating processed directory at $data_dir/processed"
        mkdir -p "$data_dir/processed"
    fi
    if [ ! -d "$data_dir/signal" ]; then
        log_message "Creating signal directory at $data_dir/signal"
        mkdir -p "$data_dir/signal"
    fi
    if [ ! -d "$data_dir/logs" ]; then
        log_message "Creating logs directory at $data_dir/logs"
        mkdir -p "$data_dir/logs"
    fi

}

start_procedure() {
    log_message "Checking for Start Signal File..."
    if [ -f "$signal_file" ]; then
        log_message "Start signal file found. Process already running... Run the stop command first and then start again."
        exit 1
    else
        log_message "Creating Start Signal File..."
        touch "$signal_file"
        log_message "File watcher started."
    fi
}

stop_procedure() {
    log_message "Checking for Start Signal File..."
    if [ -f "$signal_file" ]; then
        log_message "Start signal file found. Stopping the process."
        log_message "Removing Start Signal File..."
        rm -f "$signal_file"
        log_message "File watcher stopped."
        exit 0
    else
        log_message "Signal File not found... Script not running."
        log_message "To start the script, use the start command."
        exit 1
    fi
}

start_stop="$1"
data_dir="$2"
signal_dir="$data_dir/signal"
processed_dir="$data_dir/processed"
log_dir="$data_dir/logs"
log_file="$log_dir/file_watcher.log"
signal_file="$signal_dir/start_signal.txt"
check_and_create_directories

if [ "$start_stop" = "start" ]; then
    log_message "Starting file watcher on directory: $data_dir"
    start_procedure

    while [ -f "$signal_file" ]; do
        for file in "$data_dir"/*.parquet; do
            if [ -f "$file" ]; then
                log_message "New file detected: $file"
                ./load_retail_data_v1.sh "$file"
                if [ $? -ne 0 ]; then
                    log_message "Error processing file: $file"
                    log_message "Skipping moving file to processed directory."
                    mv "$file" "$data_dir/processed/$(basename "$file" .parquet)_error.parquet"
                    continue
                else
                    log_message "File processed successfully: $file"
                    mv "$file" "$data_dir/processed/"
                    log_message "File processed and moved to processed directory: $file"
                fi
                
            fi
        done
        sleep 10  # Check every 10 seconds
    done

elif [ "$start_stop" = "stop" ]; then
    log_message "Stopping file watcher on directory: $data_dir."
    stop_procedure
else
    log_message "Usage: ./rlt_file_watcher.sh <start|stop> <data_directory>"
    exit 1
fi
