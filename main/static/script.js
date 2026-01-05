$(document).ready(function() {
    // Initialize Nepali Datepicker
    $('.nepali-datepicker').nepaliDatePicker({
      dateFormat: 'YYYY/MM/DD',  // Set the desired date format
      disableDaysBefore: 0, 
      disableDaysAfter: 7  
    });
  });

  //form.css ***START
//   $(document).ready(function () {
//     $("#id_province").change(function () {
//         var selectedProvince = $(this).val();
//         $.ajax({
//             url: '/get-districts/',
//             data: { province: selectedProvince },
//             dataType: 'json',
//             success: function (data) {
//                 var districtSelect = $("#id_district");
//                 districtSelect.empty();
//                 districtSelect.append(new Option('Select District', ''));

//                 $.each(data, function (index, district) {
//                     districtSelect.append(new Option(district[1], district[0]));
//                 });
//             }
//         });
//     });
// });

// $(document).ready(function () {
//     $(".toggle-province").change(function () {
//       var selectedProvince = $(this).val();
//       $.ajax({
//         url: '/get-districts/',
//         data: { province: selectedProvince },
//         dataType: 'json',
//         success: function (data) {
//           var districtSelect = $("#id_district");
//           districtSelect.empty();
//           districtSelect.append(new Option('Select District', ''));

//           $.each(data, function (index, district) {
//             districtSelect.append(new Option(district, district));
//           });
//         }
//       });
//     });
//   });

  $(document).ready(function() {
    $(".toggle-vehicle").change(function() {
        if (this.checked) {
            $("#id_vehicle_number").show();  // Show the field
        } else {
            $("#id_vehicle_number").hide();  // Hide the field
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById("id_date");
    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().slice(0, 10); // Extract and format current date

    dateInput.setAttribute("data-date-start-date", formattedDate);

    
  });



  //form.css ***END


  // display.css ***START

  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("export-button").addEventListener("click", function () {
        // Collect the selected filter values
        const statusFilter = document.getElementById("current_status-filter").value;
        const officeFilter = document.getElementById("group-filter").value;

        // Send the filter values to the server via an AJAX request
        const xhr = new XMLHttpRequest();
        xhr.open("GET", `/export-to-excel/?status=${statusFilter}&office=${officeFilter}`, true);
        xhr.responseType = "blob"; // To receive a binary response
        xhr.onload = function () {
            if (this.status === 200) {
                const blob = new Blob([this.response], { type: "application/ms-excel" });
                const link = document.createElement("a");
                link.href = window.URL.createObjectURL(blob);
                link.download = "exported_data.xlsx";
                link.click();
            }
        };
        xhr.send();
    });
});

 // Function to format date as "YYYY-MM-DD"
 function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
    document.addEventListener('DOMContentLoaded', function () {
      const current_bs_date = NepaliFunctions.GetCurrentBsDate('YYYY-MM-DD');
      const searchInput = document.getElementById('searchInput');
      const tableBody = document.querySelector('table tbody');
      const rows = tableBody.getElementsByTagName('tr');
  
      searchInput.addEventListener('input', function () {
        const searchText = searchInput.value.toLowerCase();
  
        for (const row of rows) {
          let found = false;
          const cells = row.getElementsByTagName('td');
  
          for (const cell of cells) {
            if (cell.textContent.toLowerCase().includes(searchText)) {
              found = true;
              break;
            }
          }
  
          row.style.display = found ? '' : 'none';
        }
      });
      
      function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
    }
  
    // Function to set the button state
  function setButtonState($button, status) {
    const iconMappings = {
        'Gate Pass': '<i class="fas fa-check-circle fa-lg"></i>',
        'Entered': '<i class="fas fa-times-circle fa-lg"></i>',
        'Exited': '<i class="fas fa-minus-circle fa-lg"></i>',
    };
  
    const icon = iconMappings[status];
    $button.html(icon);
  }
  
  // Function to handle button click
  function handleButtonClick($button, $statusCell, $entryTimeCell, $exitTimeCell, $row, primaryKey, status) {
    // Load the color from local storage
    const storedColor = localStorage.getItem(`${primaryKey}_color`) || 'blue'; // Default to blue
    if (status === 'Exited') {
        // Prevent button click when the status is "Exited"
        console.log('Button click prevented because the status is "Exited"');
        return;
    }
  
    const now = new Date(); // Get the current time
  
  
    if (status === 'Gate Pass') {
        console.log('Changing to "Entered" state with a green icon');
        setButtonState($button, 'Entered', 'green');
        $statusCell.text('Entered');
        status = 'Entered';
        $row.removeClass('gate-pass').addClass('entered');
        $button.css('color', 'green'); // Set the color to green
  
        
  
        // Record and display the entry time
        /*const entryTimeString = now.toLocaleTimeString();
        $entryTimeCell.text(entryTimeString);
        
        $exitTimeCell.text(''); // Clear exit time*/
    } else if (status === 'Entered') {
        console.log('Changing to "Exited" state with a red icon');
        setButtonState($button, 'Exited', 'red');
        $statusCell.text('Exited');
        status = 'Exited';
        $row.removeClass('entered').addClass('exited');
        $button.css('color', 'red'); // Set the color to red
        // Record and display the exit time
       /* const entryTimeString = $entryTimeCell.text();
        const exitTimeString = now.toLocaleTimeString();
        $entryTimeCell.text(entryTimeString); // Preserve the entry time
  
        $exitTimeCell.text(exitTimeString);*/
    } else {
        console.log('Changing back to "Gate Pass" state with a blue icon');
        setButtonState($button, 'Gate Pass', 'blue');
        $statusCell.text('Gate Pass');
        status = 'Gate Pass';
        $row.removeClass('exited').addClass('gate-pass');
        $button.css('color', 'blue'); // Set the color to blue
  
        // Clear the entry and exit times
       /* $entryTimeCell.text('');
        $exitTimeCell.text('');*/
    }
  
    console.log('Final Current Status:', status);
  
    // Save the status in local storage
    localStorage.setItem(primaryKey, status);
    localStorage.setItem(`${primaryKey}_color`, $button.css('color'));
  
  
    $.ajax({
        url: '/update_status/',  // URL endpoint to handle the status update
        method: 'POST',
        data: {
            'primary_key': primaryKey,
            'new_status': status
        },
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function (response) {
            // Handle the response from the server if needed
        },
        error: function (error) {
            console.error('Error:', error);
        }
    });
  }
  
  // Function to update entry and exit times
  function updateEntryExitTimes($row, status) {
    const $entryTimeCell = $row.find('.entry-time');
    const $exitTimeCell = $row.find('.exit-time');
  
    if (status === 'Entered') {
      const entryTime = new Date();
      $entryTimeCell.text(entryTime.toLocaleString());
    } else if (status === 'Exited') {
      if ($entryTimeCell.text() === '') {
        // Only set exit time if entry time is available
        $exitTimeCell.text('');
      } else {
        const exitTime = new Date();
        $exitTimeCell.text(exitTime.toLocaleString());
      }
    } else {
      $entryTimeCell.text(''); // Clear entry time
      $exitTimeCell.text(''); // Clear exit time
    }
  }
  
  
  // Function to calculate and update the duration of stay
  function updateDurationOfStay($row) {
    const $entryTime = $row.find('.entry-time');
    const $exitTime = $row.find('.exit-time');
    const $durationElement = $row.find('.duration-of-stay');
  
    const entryTimeString = $entryTime.text();
    const exitTimeString = $exitTime.text();
  
    if (entryTimeString && exitTimeString) {
      const entryTime = new Date(entryTimeString);
      const exitTime = new Date(exitTimeString);
      const duration = calculateDuration(entryTime, exitTime);
  
      $durationElement.text(duration);
    } else {
      $durationElement.text('N/A'); // Display "N/A" if entry or exit time is missing
    }
  }
  
  // Function to calculate and return the duration of stay
  function calculateDuration(entryTime, exitTime) {
    if (!entryTime || !exitTime) {
      return 'N/A';
    }
  
    const durationMs = exitTime - entryTime;
  
    // Calculate hours, minutes, and seconds
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    //const hours = Math.floor(durationMs / 3600000);
    //const minutes = Math.floor((durationMs % 3600000) / 60000);
    //const seconds = Math.floor((durationMs % 60000) / 1000);
  
    return `${days} days {hours} hours ${minutes} minutes ${seconds} seconds`;
  }
  
  
  $('.status-button').each(function () {
    const $button = $(this);
    const $statusCell = $button.closest('tr').find('.status');
    
  
    const status = $statusCell.data('status');
    const $row = $button.closest('tr');
    const primaryKey = $row.find('.primary-key').data('primary-key');
  
    // Define $entryTimeCell and $exitTimeCell here
    const $entryTimeCell = $row.find('.entry-time');
    const $exitTimeCell = $row.find('.exit-time');
  
    // Additional code to get the item date
    const itemDateText = $row.find('.date').text();
    const itemDateParts = itemDateText.split('/');
    const itemDate = new Date(`${itemDateParts[0]}-${itemDateParts[1]}-${itemDateParts[2]}`);
    const formattedItemDate = formatDate(itemDate);
  
    // Add console logs for debugging
    //console.log('Current BS Date:', current_bs_date);
    //console.log('Item Date:', formattedItemDate);
  
  
    //const itemDate = new Date(itemDateText);
  
    // Get the saved status from local storage
    const savedStatus = localStorage.getItem(primaryKey);
  
    
  
    if (savedStatus) {
        // Use the saved status if available
        setButtonState($button, savedStatus, savedStatus === 'Exited' ? 'red' : (savedStatus === 'Entered' ? 'green' : 'blue'));
        $statusCell.text(savedStatus);
        $row.removeClass('gate-pass entered exited').addClass(savedStatus.toLowerCase());
  
        // Display entry and exit times if available
        updateEntryExitTimes($row, savedStatus);
  
      }
  
    const storedColor = localStorage.getItem(`${primaryKey}_color`);
          if (storedColor) {
              $button.css('color', storedColor);
          }
  
          $button.hover(
            function () {
              const $icon = $button.find('i'); // Get the icon element
              const iconClass = $icon.attr('class');
              const buttonColor = $button.css('color');
              if (iconClass.includes('fa-check-circle') ) {
                $icon.attr('title', 'Enter');
              } else if (iconClass.includes('fa-times-circle') ) {
                $icon.attr('title', 'Exit');
              } else if (iconClass.includes('fa-minus-circle') ) {
                $icon.attr('title', 'Discard');
              }
            },
            function () {
              const $icon = $button.find('i'); // Get the icon element
              $icon.attr('title', ''); // Clear the title on hover out
            }
          );
  
          //Check if the current_bs_date is same as item.date
          if (current_bs_date == formattedItemDate){
            
            $button.click(function (){
              handleButtonClick($button, $statusCell, $entryTimeCell, $exitTimeCell, $row, primaryKey, status);
              updateDurationOfStay($row);
  
            });
          } else{
            // Display a message or disable the button if the dates are not the same
            $button.attr('disabled', true); // Disable the button
            $button.css('cursor', 'not-allowed'); // Change cursor style
            $button.attr('title', 'Status can only be updated on the specified date.'); // Display a tooltip
  
          }
  
  
    
  
  });
  
  // Initial update of duration of stay
  $('table tbody tr').each(function () {
    const $row = $(this);
    updateDurationOfStay($row);
  });
  
  
    });

    $(document).ready(function() {
        $('.detail-button').click(function() {
          const $row = $(this).closest('tr');
          const $detailedData = $row.find('.detailed-data');
    
          // Toggle the display of detailed data
          $detailedData.toggle();
        });
      });

      $(document).ready(function() {
        $(".delete-item").click(function() {
          var itemId = $(this).data("item-id");
          var $row = $(this).closest("tr");
    
          // Show a confirmation dialog
          var confirmDelete = confirm("Are you sure you want to delete this item?");
          
          if (confirmDelete) {
            // User clicked OK in the confirmation dialog
            $.ajax({
              url: '/delete-form/' + itemId + '/',  // Replace with your delete view URL
              method: 'DELETE',
              headers: {
                'X-CSRFToken': getCookie('csrftoken')
              },
              success: function() {
                // Remove the row from the table on success
                $row.remove();
              },
              error: function(error) {
                console.error('Error:', error);
              }
            });
          }
        });
    
        function getCookie(name) {
          var value = "; " + document.cookie;
          var parts = value.split("; " + name + "=");
          if (parts.length === 2) return parts.pop().split(";").shift();
        }
      });

      document.addEventListener('DOMContentLoaded', function () {
        const rows = document.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
          if (row.classList.contains('exited')) {
            const entryTime = row.querySelector('.entry-date').textContent;
            const exitTime = row.querySelector('.exit-time').textContent;
            
            if (entryTime && exitTime) {
              const entryTimestamp = new Date(entryTime).getTime();
              const exitTimestamp = new Date(exitTime).getTime();
              const timeDifference = (exitTimestamp - entryTimestamp) / 1000; // Time difference in seconds
              const timeSpentCell = row.querySelector('.time-spent');
              timeSpentCell.textContent = formatTimeDifference(timeDifference);
            }
          }
    
           // Convert Gregorian date to Nepali date
           const dateCell = row.querySelector('.date');
           const gregorianDate = new Date(dateCell.textContent);
           const nepaliDate = NepaliFunctions.ad2bs(gregorianDate.getFullYear(), gregorianDate.getMonth() + 1, gregorianDate.getDate());
           const nepaliDateString = `${nepaliDate.bsYear}/${nepaliDate.bsMonth}/${nepaliDate.bsDate}`;
           dateCell.textContent = nepaliDateString;
    
    
        });
      });

      $(document).ready(function() {
        $('#group-filter').on('change', function() {
          var selectedGroup = $(this).val();
          console.log('Selected Group:', selectedGroup);
          if (selectedGroup === 'all') {
            // Show all rows if "all" is selected
            $('table tbody tr').show();
          } else {
              // Hide rows that don't match the selected group
            $('table tbody tr').each(function() {
              var itemGroup = $(this).find('.group').text(); // Get the group from the table cell
              if (itemGroup === selectedGroup) {
                $(this).show();
              } else {
                $(this).hide();
              }
            });
          }
        });
        $('#current_status-filter').on('change', function () {
          var selectedStatus = $(this).val();
          console.log('Selected Status:', selectedStatus);
          if (selectedStatus === 'all') {
            // Show all rows if "all" is selected
            $('table tbody tr').show();
          } else {
            // Hide rows that don't match the selected status
            $('table tbody tr').each(function () {
              var itemStatus = $(this).find('.status').text();
              if (itemStatus === selectedStatus) {
                $(this).show();
              } else {
                $(this).hide();
              }
            });
          }
        });
        $('#consumable_status-filter').on('change', function () {
          var selectedStatus = $(this).val();
          console.log('Selected Status:', selectedStatus);

          if (selectedStatus === 'all') {
            // Show all rows if "all" is selected
            $('table tbody tr').show();
          } else {
            // Hide rows that don't match the selected status
            $('table tbody tr').each(function () {
              var itemStatus = $(this).find('.consumable').text();
              if (itemStatus === selectedStatus) {
                $(this).show();
              } else {
                $(this).hide();
              }
            });
          }
        });
      });


      // display.css ***END