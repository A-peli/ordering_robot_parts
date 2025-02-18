from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    browser.configure(
        slowmo=10,
    )
    """
    Order robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as PDF file. 
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    orders = get_orders()
    order_loop(orders)
    archive_receipts()
    
def open_robot_order_website():
    #opens robot order website
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
def get_orders():
    #downloads csv and reads it and saves it as variable#
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv")
    print (orders)
    return orders

def close_annoying_modal():
    #clicks away from the annoying prompt
    page = browser.page()
    page.click("button:text('Ok')")

def order_loop(orders):
    #loops through the orders table and feeds it into fill_the_form
    for row in orders:
        order_number = fill_the_form(row)
        submit_order(order_number)
        

def fill_the_form(row):
    #goes through the page and fills the order form with data from table(orders)
    #screenshots the preview image of the robot and saves it
    page = browser.page()
    order_number = str(row['Order number'])
    head = str(row['Head'])
    body = str(row['Body'])
    legs = row['Legs']
    address = str(row['Address'])
    close_annoying_modal()
    page.select_option("#head", head)
    page.click("#id-body-"+body)
    page.fill('input[placeholder="Enter the part number for the legs"]', legs)
    page.fill("#address", address)
    return order_number
""" "#id-body-" """
def submit_order(order_number):
    """ clicks the order button and if errors pop up, it will try again """
    page = browser.page()
    while True:
        page.click("#order")
        if check_errors():
            process_order(order_number)
            break
def check_errors():
    page = browser.page()
    error_locator = page.locator("div.alert.alert-danger")
    if error_locator.count() > 0 and error_locator.is_visible():
        return False
    return True


def process_order(order_number):
    page = browser.page()
    screenshot = screenshot_robot(order_number)
    pdf_receipt = store_receipt_as_pdf(order_number)
    embed_screenshot_to_receipt(screenshot, pdf_receipt)
    page.click("#order-another")

def screenshot_robot(order_number):
    page = browser.page()
    file_path = 'output/screenshots/'+order_number+'.png'
    page.locator("#robot-preview-image").screenshot(path=file_path)
    return file_path

def store_receipt_as_pdf(order_number):
    print(order_number)
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    file_path = "output/Receipts/order"+order_number+"receipt.pdf"
    pdf.html_to_pdf(receipt_html, file_path)
    return file_path

def embed_screenshot_to_receipt(screenshot, pdf_receipt):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot], 
        target_document=pdf_receipt, 
        append=True)
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/Receipts", "receipts.zip", include="*.pdf")