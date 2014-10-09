import os
import time
import urllib
from ghost import Ghost
from datetime import datetime

import logging
#Ghost.py and PySide required
#mkvirtualenv paypalhistoryexport --no-site-packages --python=/usr/bin/python2.7
#workon paypalhistoryexport
#pip install Ghost.py PySide
#sudo ulimit -SHn 65535
#sudo sh -c "ulimit -SHn 65535"
#python runexport.py

from settings import PAYPAL_USERNAME, PAYPAL_NAME, PAYPAL_PASSWORD, EXPORT_DIRECTORY, CACHE_DIRECTORY, START_DATE, END_DATE

def getHistoryListing(ghost):
    #GOTO history page
    page, resources = ghost.open('https://www.paypal.com/ie/cgi-bin/webscr?cmd=_history&nav=0.3')
    ghost.wait_for_text("History")



    ghost.click('#dateoptions')

    ghost.evaluate("""  var elem = document.getElementById("from_date");
                        elem.value = "%s";
                        elem = document.getElementById("to_date");
                        elem.value = "%s";
                    """ % (START_DATE, END_DATE))

    page, resources = ghost.evaluate("document.getElementById('show').click();", expect_loading=True)
    #page, resources = ghost.fire_on("form[name=history]", "submit", expect_loading=True)
    ghost.wait_for_page_loaded()

    #only show payments sent
    # ghost.evaluate('''
    #     var name_input = document.createElement('input');
		# name_input.setAttribute('name', 'name');
    #     name_input.setAttribute('id',   'name');
    #     name_input.setAttribute('value',   'filter_4');
    #     document.getElementsByName("history")[0].appendChild(name_input);
		# ''')
    #
    # page, resources = ghost.evaluate("document.getElementById('show').click();", expect_loading=True)
    ghost.evaluate('document.getElementsByName("filter_4")[0].click()',expect_loading=True)
    #page, resources = ghost.fire_on("form[name=history]", "submit", expect_loading=True)
    ghost.wait_for_page_loaded()


def RunExport():
    ghost = Ghost(viewport_size=(1200, 2400), display=False, wait_timeout=30, cache_dir=CACHE_DIRECTORY)#, log_level=logging.ERROR

    #
    #login_password
    #submit.x
    #submit
    page, resources = ghost.open('https://www.paypal.com/ie/cgi-bin/webscr?cmd=_login-run')

    result, resources = ghost.fill("form[name=login_form]", {
            "login_email": PAYPAL_USERNAME,
            "login_password": PAYPAL_PASSWORD
        })
    page, resources = ghost.fire_on("form[name=login_form]", "submit", expect_loading=True)
    result, resources = ghost.wait_for_page_loaded()
    #wait for 10 seconds
    #time.sleep(10)

    page, resources = ghost.open('https://www.paypal.com/ie/cgi-bin/webscr?cmd=_account')


    result, resources = ghost.wait_for_text("Welcome, %s" % PAYPAL_NAME)


    getHistoryListing(ghost)

    first_run = True
    #get the next url
    #print ghost.evaluate('document.querySelectorAll("#tableWrapperID .pagination:nth-child(1) a.btnLink");')[0]
    nav_links_eval = """
                      var links = document.querySelectorAll(".pagination a.btnLink");
                        links.length;
                    """
    nav_links = ghost.evaluate(nav_links_eval)
    page_count = 0
    #transaction_list_url = resources[0].url
    #print transaction_list_url
    while nav_links[0] > 0 or first_run==True:
        first_run = False
        page_count = page_count + 1
        ghost.capture_to(os.path.join(EXPORT_DIRECTORY,'filteredhistory%d.png' % page_count), selector="body")

        transaction_urls = ghost.evaluate("""
                            var links = document.querySelectorAll("#transactionTable tr.primary td.detailsNoPrint a");
                            var listRet = [];
                            for (var i=0; i<links.length; i++){
                                listRet.push(links[i].href);
                            }
                            listRet;
                            """)

        transaction_count = 0
        for transaction_href in transaction_urls[0]:
            transaction_count = transaction_count + 1
            #print urllib.unquote(transaction_href)

            page, resources = ghost.open(urllib.unquote(transaction_href))
            ghost.wait_for_page_loaded()
            payee_name = None
            date_string = None
            date = ghost.evaluate("""
                           document.querySelectorAll("#historyMiniLog tbody tr")[2].querySelectorAll('td')[0].innerHTML;
                        """)
            if date and date[0]:
                date_string = date[0].replace('&nbsp;','')

            payee = ghost.evaluate("""
                           document.querySelectorAll("#historyMiniLog tbody tr")[2].querySelectorAll('td')[1].innerHTML;
                        """)
            if payee and payee[0]:
                payee_name = payee[0].replace('&nbsp;','')

            if payee_name and date_string:

                date_object = datetime.strptime(date_string, '%d-%b-%Y')
                date_string=datetime.strftime(date_object,'%Y-%m-%d')
                print 'page %d transaction %d [%s - %s]' % (page_count, transaction_count, date_string,payee_name)
                ghost.capture_to(os.path.join(EXPORT_DIRECTORY,'%s_%s.png' % (date_string,payee_name )), selector="#xptContentMain")
            else:
                ghost.capture_to(os.path.join(EXPORT_DIRECTORY,'no date and payee - page-%d_ transaction %d.png' % (page_count,transaction_count )), selector="#xptContentMain")
                print 'could not save'


        getHistoryListing(ghost)

        #we're back on page one now so we need to get back to where we were
        for x in range(0, page_count):
            ghost.evaluate("""
                document.getElementById('myAllTextSubmitID').name = 'next';
                document.getElementById('myAllTextSubmitID').value = 'Next';
                document.forms.history.submit();
                """, expect_loading=True)
            ghost.wait_for_page_loaded()
        #transaction_list_url = resources[0].url
        nav_links = ghost.evaluate(nav_links_eval)

if __name__ == "__main__":
    RunExport()
