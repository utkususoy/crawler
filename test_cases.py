from main import UrlScraper

if __name__ == "__main__":
    url = "https://www.navalnews.com/category/naval-news/page/2/" #done, 19 haber recall++
    url = "https://www.navalnews.com/" #done 20 ++
    url = "https://www.navytimes.com/" #done 68 ++
    url = "https://www.navytimes.com/news/pentagon-congress/" #incele
    # url = "https://www.navy.mil/Press-Office/" #
    url = "https://www.navy.mil/Press-Office/Press-Releases/display-pressreleases/Article/3652564/secnav-del-toro-meets-with-key-leaders-during-travel-through-europe/"
    url = "https://www.centcom.mil/MEDIA/NEWS-ARTICLES/" #done +
    url = "https://www.centcom.mil/" #done recall oriented. +
    url2 = "https://www.military.com/navy" #done, head çıkarıldı #35
    #url = "https://www.businessinsider.com/news" #done, 65 ++
    # url = "https://indianexpress.com/"#done recall+
    #url = "https://www.voanews.com/a/ships-aircraft-search-for-missing-navy-seals-after-mission-to-seize-iranian-missile-parts/7440990.html" #done recall+
    # url = "https://www.defensenews.com/naval/" #done, recall+
    # url = "https://www.defensenews.com/"
    # url = "https://www.navaltoday.com/" #done, 44 recall+
    # url = "https://www.miragenews.com/" #54 Select Top 3 Vote +++

    # url = "https://www.al-monitor.com/" # 31 stv3++
    # url = "https://www.shephardmedia.com/news/naval-warfare/turkish-navy-looks-to-advance-maritime-power-with-2024-fleet-expansion/" #6 news 18 found ++
    # url = "https://www.shephardmedia.com/" #3 news 9 found ++

    #url = "https://www.defenseone.com/"
    # url = "https://www.alhurra.com/" # st3v +++

    # tr news
    # url = "https://www.hurriyetdailynews.com/"  # 69 + st3v +++
    # url = "https://www.aa.com.tr/en/turkiye/turkiye-hosting-eastern-mediterranean-2023-invitation-naval-exercise/3058764"  # news url-indicator dan çıkarıldı
    url = "https://www.bbc.com/"
    url = "https://www.sabah.com.tr/"
    # url = "https://www.dailysabah.com/war-on-terror"  # st3v +++
    url = "https://www.ntvspor.net/"

    # gr news
    #url = "https://www.naftikachronika.gr/" #st3v +++
    # url = "https://e-nautilia.gr/" #st3v +++
    # url = "https://www.naftikachronika.gr/latest/" #stv3 +++
    # url = "https://www.naftemporiki.gr/maritime/" #st3v +++
    # url = "https://www.isalos.net/" #st3v +++
    # url = "https://www.capital.gr/tag/nautilia/" #st3v +++
    # url = "https://www.maritimes.gr/el/"
    # url = "https://www.pno.gr/"
    # url = "https://tralaw.gr/category/nautika-nea/"
    # url = "https://www.tanea.gr/tag/%CE%BD%CE%B1%CF%85%CF%84%CE%B9%CE%BA%CE%BF%CE%AF/"
    # url = "https://www.alithia.gr/eidiseis" #st3v +++
    # url = "https://hellenicnavy.gr/" #st3v +++ 1+2=35 no-punc ++
    # url = "https://www.onalert.gr/" #st3v +++ no-punc ++

    # ar news
    url = "https://asharq.com/"
    # url = "https://asharq.com/defense/78370/%D8%A7%D9%84%D8%A3%D8%B3%D8%B7%D9%88%D9%84-%D8%A7%D9%84%D8%B4%D8%A8%D8%AD%D9%8A-%D8%A7%D9%84%D8%A3%D9%85%D9%8A%D8%B1%D9%83%D9%8A-%D9%8A%D9%86%D8%AA%D9%87%D9%8A-%D9%85%D9%86-%D8%A3%D9%88%D9%84-%D8%A7%D9%86%D8%AA%D8%B4%D8%A7%D8%B1-%D8%AA%D8%B4%D8%BA%D9%8A%D9%84%D9%8A/" #st3v +++
    url = "https://www.arab48.com/"
    # url = "https://www.arab48.com/%D8%A7%D9%84%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1-%D8%B9%D8%A7%D8%AC%D9%84%D8%A9/2024/01/26/%D8%A7%D9%84%D8%AD%D9%88%D8%AB%D9%8A%D9%88%D9%86-%D8%A7%D8%B3%D8%AA%D9%87%D8%AF%D9%81%D9%86%D8%A7-%D8%B3%D9%81%D9%8A%D9%86%D8%A9-%D9%86%D9%81%D8%B7-%D8%A8%D8%B1%D9%8A%D8%B7%D8%A7%D9%86%D9%8A%D8%A9-%D9%81%D9%8A-%D8%AE%D9%84%D9%8A%D8%AC-%D8%B9%D8%AF%D9%86-%D8%A8%D8%B5%D9%88%D8%A7%D8%B1%D9%8A%D8%AE-%D8%A8%D8%AD%D8%B1%D9%8A%D8%A9-%D8%A3%D8%AF%D8%AA-%D8%A5%D9%84%D9%89-%D8%A7%D8%AD%D8%AA%D8%B1%D8%A7%D9%82%D9%87%D8%A7" #st3v +++
    url = "https://www.aljazeera.net/"
    url = "https://www.aljazeera.net/news/2024/1/22/%D8%A7%D9%84%D8%A8%D8%AD%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D8%A3%D9%85%D9%8A%D8%B1%D9%83%D9%8A%D8%A9-%D9%84%D9%85-%D9%86%D8%B9%D8%AB%D8%B1-%D8%B9%D9%84%D9%89-%D8%AC%D9%86%D8%AF%D9%8A%D9%8A%D9%92%D9%86"
    url = "https://www.i24news.tv/ar"
    url = "https://www.i24news.tv/ar/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1/middle-east/1706089551-%D9%87%D8%B0%D9%87-%D8%A7%D9%84%D9%82%D9%88%D8%A9-%D8%A7%D9%84%D8%A8%D8%AD%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D8%A3%D9%85%D8%B1%D9%8A%D9%83%D9%8A%D8%A9-%D8%A7%D9%84%D8%AC%D8%AF%D9%8A%D8%AF%D8%A9-%D8%A7%D9%84%D8%AA%D9%8A-%D8%AA%D9%86%D8%B4%D8%B7-%D8%A8%D8%A7%D9%84%D8%A8%D8%AD%D8%B1-%D8%A7%D9%84%D8%A3%D8%AD%D9%85%D8%B1-%D9%88%D9%85%D8%B6%D9%8A%D9%82-%D9%87%D8%B1%D9%85%D8%B2"
    url = "https://ar.mehrnews.com/"
    url = "https://ar.mehrnews.com/news/1940752/%D9%82%D8%B1%D9%8A%D8%A8%D8%A7-%D8%A7%D9%86%D8%B6%D9%85%D8%A7%D9%85-%D8%AD%D9%88%D8%A7%D9%85%D8%A7%D8%AA-%D9%85%D8%B2%D9%88%D8%AF%D8%A9-%D8%A8%D8%B5%D9%88%D8%A7%D8%B1%D9%8A%D8%AE-%D8%A8%D8%B9%D9%8A%D8%AF%D8%A9-%D8%A7%D9%84%D9%85%D8%AF%D9%89-%D8%A5%D9%84%D9%89-%D8%A7%D9%84%D9%82%D9%88%D8%A7%D8%AA"
    url = "https://www.skynewsarabia.com/"
    url = "https://www.skynewsarabia.com/middle-east/1688076-%D8%A7%D9%84%D8%A8%D8%AD%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D8%A7%D9%94%D9%85%D9%8A%D8%B1%D9%83%D9%8A%D8%A9-%D8%AA%D8%B9%D8%AA%D8%B1%D8%B6-%D8%B5%D9%88%D8%A7%D8%B1%D9%8A%D8%AE-%D8%A7%D9%84%D8%A8%D8%AD%D8%B1-%D8%A7%D9%84%D8%A7%D9%94%D8%AD%D9%85%D8%B1"
    url = "https://www.saba.ye/ar"
    url = "https://nashwannews.com/"
    url = "https://nashwannews.com/265925/%D8%B4%D8%A7%D9%87%D8%AF-%D8%A7%D9%84%D8%A8%D8%AD%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D9%87%D9%86%D8%AF%D9%8A%D8%A9-%D8%AA%D9%86%D8%B4%D8%B1-%D8%B5%D9%88%D8%B1-%D8%A7%D9%84%D8%B3%D9%81%D9%8A%D9%86%D8%A9"
    url = "https://kech24.com/"
    url = "https://kech24.com/%D8%A5%D8%B7%D9%84%D8%A7%D9%82-%D8%AD%D9%85%D9%84%D8%A9-%D8%A7%D8%B3%D8%AA%D9%83%D8%B4%D8%A7%D9%81-%D8%B9%D9%84%D9%85%D9%8A-%D8%B9%D8%A8%D8%B1-%D8%A7%D9%84%D8%B3%D9%81%D9%8A%D9%86%D8%A9-%D8%A7%D9%84%D8%A8%D8%AD%D8%AB%D9%8A%D8%A9-%D8%A7%D9%84%D9%85%D8%BA%D8%B1%D8%A8%D9%8A%D8%A9-%D8%AD%D8%B3%D9%86-%D8%A7%D9%84%D9%85%D8%B1%D8%A7%D9%83%D8%B4%D9%8A.html"
    url = "https://www.4may.net/news/107605"
    url = "https://www.4may.net/"

    url = "https://www.miragenews.com/"

    us = UrlScraper()
    res = us.unknown_main(source_url=url, print_eliminated=True, print_all=True)

    print("\nCOMPREHENSIVE RESULTS:\n")
    print(res)
    print(len(res))