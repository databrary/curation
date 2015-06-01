require 'Datavyu_API.rb'
require 'csv'


###################################################################################
# USER EDITABLE SECTION.  PLEASE PLACE YOUR SCRIPT BETWEEN BEGIN AND END BELOW.
###################################################################################

begin
  filedir = File.expan_path("~/curation/data/<PATH_TO_DATAVYU_FILES")
  filenames = Dir.new(filedir).entries

  dir = File.expand_path("~/curation/data/datavyu_out")
  out_file = File.new(dir + "/<OUTPUT>.csv", "w")    

  for file in filenames
    if file.include?(".opf") and file[0].chr != '.'

      puts "LOADING DATABASE: " + filedir+file
      $db,proj = load_db(filedir+file)
      puts "SUCCESSFULLY LOADED"

      id = file.split(' ')[0]
      task = getVariable("Tasks")

      out_file.syswrite(id+",")
      for taskcell in task.cells
        if taskcell.task == "n3" #this would change based on the codes you're using
          out_file.syswrite("3 Neutral Box,"+taskcell.onset.to_s+","+taskcell.offset.to_s+",")
        end
        if taskcell.task == "t2" #this would change based on the codes you're using
          out_file.syswrite("2 Typical Box,"+taskcell.onset.to_s+","+taskcell.offset.to_s+",")
        end        
        if taskcell.task == "t3" #this would change based on the codes you're using
          out_file.syswrite("3 Typical Box,"+taskcell.onset.to_s+","+taskcell.offset.to_s+",")
        end        
        if taskcell.task == "l3" #this would change based on the codes you're using
          out_file.syswrite("3 Location,"+taskcell.onset.to_s+","+taskcell.offset.to_s+",")
        end
      end  
      out_file.syswrite("\n")

    end
    puts "done"
  end
end