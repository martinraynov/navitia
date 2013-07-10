#include "ed/data.h"
#include "ed/gtfs_parser.h"
#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE test_ed
#include <boost/test/unit_test.hpp>
#include <string>
#include "config.h"
#include "ed/build_helper.h"

const std::string gtfs_path = "/ed/gtfs";


BOOST_AUTO_TEST_CASE(connection_transformer){
    ed::types::Connection connection;
    ed::types::StopPoint* origin = new ed::types::StopPoint();
    ed::types::StopPoint* destination = new ed::types::StopPoint();

    origin->idx = 8;
    destination->idx = 523;
    
    connection.id = "12";
    connection.idx = 32;
    connection.uri = "connection_12";
    connection.departure_stop_point = origin;
    connection.destination_stop_point = destination;
    connection.duration = 10;
    connection.max_duration = 15;
    connection.connection_kind = ed::types::ConnectionType::Walking;

    navitia::type::Connection connection_n = connection.get_navitia_type();

    BOOST_CHECK_EQUAL(connection_n.idx, connection.idx);
    BOOST_CHECK_EQUAL(connection_n.id, connection.id);
    BOOST_CHECK_EQUAL(connection_n.uri, connection.uri);
    BOOST_CHECK_EQUAL(connection_n.departure_idx, origin->idx);
    BOOST_CHECK_EQUAL(connection_n.destination_idx, destination->idx);
    BOOST_CHECK_EQUAL(connection_n.duration, connection.duration);
    BOOST_CHECK_EQUAL(connection_n.max_duration, connection.max_duration);

    delete destination;
    delete origin;
}


BOOST_AUTO_TEST_CASE(stop_area_transformer){
    ed::types::StopArea stop_area;

    stop_area.id = "12";
    stop_area.idx = 32;
    stop_area.uri = "stop_area_12";
    stop_area.name = "somewhere";
    stop_area.comment = "comment";

    stop_area.coord.set_lon(-54.08523);
    stop_area.coord.set_lat(5.59273);

    navitia::type::StopArea stop_area_n = stop_area.get_navitia_type();

    BOOST_CHECK_EQUAL(stop_area_n.idx, stop_area.idx);
    BOOST_CHECK_EQUAL(stop_area_n.id, stop_area.id);
    BOOST_CHECK_EQUAL(stop_area_n.uri, stop_area.uri);
    BOOST_CHECK_EQUAL(stop_area_n.name, stop_area.name);
    BOOST_CHECK_EQUAL(stop_area_n.comment, stop_area.comment);
    BOOST_CHECK_EQUAL(stop_area_n.coord.lon(), stop_area.coord.lon());
    BOOST_CHECK_EQUAL(stop_area_n.coord.lat(), stop_area.coord.lat());
}

BOOST_AUTO_TEST_CASE(validity_pattern){
    boost::gregorian::date begin;
    begin=boost::gregorian::date_from_iso_string("201303011T1739");
    ed::types::ValidityPattern *vp;
    vp = new  ed::types::ValidityPattern(begin, "01");
    BOOST_CHECK_EQUAL(vp->days.to_ulong(), 1);
}