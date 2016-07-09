var names_state = {};
d3.tsv("static/data_annexe/us-state-names.tsv", function(error, data) {
    data.forEach(function(p) {
        //console.log("total : " + p.code + '---' + p.name);
        names_state[p.code] = p.name;
        //console.log("total : " + names_state[p.code] + '--' + p.code);
    });
});



var dataset = [];

var form = d3.select("#myform").selectAll("svg").selectAll("li")
form.on("mouseover", function(d) {
    console.log(val)
})

function handleClick(event) {
    draw(document.getElementById("myVal").value)
    return false;
}

function draw(val) {
    d3.select("#valtext").append("li");
    dataset.push(val);
    var p = d3.select("#valtext").selectAll("li")
        .data(dataset)
        .text(function(d, i) {
            return d;
        })

}

Array.prototype.contains = function(obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
}

var list = []
var list_sentiment = []

// function get_tweets() {
//     //make ajax call
//     var url = "http://127.0.0.1:5007/tweets/analytics?hastag=#MAGA" 
//     d3.json(url, function(json, error) {});
//     return json
// }

queue()
    .defer(d3.json, "/tweets/analytics")
    .defer(d3.json, "static/geojson/us-states.json")
    .await(makeGraphs);

function makeGraphs(error, projectsJson, statesJson) {
    //Clean projectsJson data
    var tweetAnalytics = projectsJson;
    //console.log(word_count)
    //console.log(statesJson)
    var dateFormat = d3.time.format("%Y-%m-%dT%H%M");
    var counts;

    tweetAnalytics.forEach(function(d) {

        d["Timestamp"] = new Date(d["Timestamp"]);
        d["Sentiment"] = d["Sentiment"]
        d["SentimentText"] = d["SentimentText"];
        d["State"] = d["State"]
            //counts += d["SentimentText"]

    });

    // Create a Crossfilter instance
    // JS library to deal with large amount of data
    var ndx = crossfilter(tweetAnalytics);

    // Define Dimensions
    var stateDim = ndx.dimension(function(d) {
        return d["State"];
    });
    var posTweetDim = ndx.dimension(function(d) {
        return d["Sentiment"];
    });

    // var timeDimension = ndx.dimension(function (d) { return d3.time.hour(d["Timestamp"]); });
    var timeDimension = ndx.dimension(function(d) {
        return d["Timestamp"];
    });

    var volumeByHour = ndx.dimension(function(d) {
        return d3.time.hour(d["Timestamp"]);
    });
    var volumeByDayGroup = volumeByHour.group().reduceCount(function(d) {
        return d["Timestamp"];
    });

    var maxDate = new Date("2016-06-08");
    var minDate = new Date("2016-06-07");

    var numProjectsByDate = timeDimension.group();


    // console.log("positive : " + minDate);
    // console.log("negative : " + maxDate);


    // Information by state
    var tweetsByState = stateDim.group();
    var nbtweetsByState = stateDim.group().length;
    var posTweetByState = stateDim.group().reduceSum(function(d) {
        return d["Sentiment"];

    });

    var allstate = stateDim.group()
    var totTweetByState = stateDim.group().reduceSum(function(d) {
        return 1;
    });
    var textByState = stateDim.group().reduceSum(function(d) {
        return d["SentimentText"] + " ";
    });
    var all = ndx.groupAll();
    var posSentiment = ndx.groupAll().reduceSum(function(d) {
        return d["Sentiment"];
    });

    // Put a ratio instead of a value
    var max_state = posTweetByState.value;

    // Charts
    // var tweetsTimeChart = dc.barChart("#tweetsTime-chart");
    var tweetsTimeChart = dc.lineChart("#tweetsTime-chart");
    var ratioPieChart = dc.pieChart("#ratio-sent-piechart")
    var usChart = dc.geoChoroplethChart("#us-chart");
    var numberProjectsND = dc.numberDisplay("#number-projects-nd");

    // d3.selectAll('#us-char').on('click',world_cloud)
    var us_char = d3.select('#us-chart')
        //us_char.on('click',world_cloud)

    var sentiment = ndx.dimension(function(d) {
        if (d["Sentiment"] == 1)
            return "Positive";
        else
            return "Negative";
    });

    var sentimentGroup = sentiment.group();


    // time graph
    tweetsTimeChart.width(600)
        .height(160)
        .margins({
            top: 10,
            right: 50,
            bottom: 30,
            left: 50
        })
        .dimension(timeDimension)
        .group(numProjectsByDate)
        .transitionDuration(500)
        .elasticY(true)
        .x(d3.time.scale().domain([minDate, maxDate])) // scale and domain of the graph
        .xAxis();


    ratioPieChart.width(300)
        .height(300)
        .dimension(sentiment)
        .group(sentimentGroup)
        .title(function(d) {
            return d.value;
        })
        .renderlet(function(chart) {
            chart.selectAll('g').on("click", function(p) {
                if (p != null) {
                    var this_sentiment = p.data.key
                    console.log(this_sentiment)
                    if (window.list_sentiment.includes(this_sentiment)) {
                        window.list_sentiment = window.list_sentiment.filter(function(el) {
                            return el != this_sentiment;
                        })
                    } else {
                        window.list_sentiment.push(this_sentiment)
                    }
                    world_cloud()
                }

            })
        });

    numberProjectsND
        .formatNumber(d3.format("d"))
        .valueAccessor(function(d) {
            return d;
        })
        .group(all);

    usChart.width(1000)
        .height(330)
        .dimension(stateDim)
        .group(posTweetByState)
        .colors(["#E10000", "#D10F0F", "#C01C1C", "#A82828", "#823131", "#4D894F", "#41A444", "#2AB72F", "#0A9D0F", "#0C7B00"])
        .colorDomain([0, 20])
        .overlayGeoJson(statesJson["features"], "state", function(d) {
            return d.properties.name;

        })
        .projection(d3.geo.albersUsa()
            .scale(600)
            .translate([320, 150])
        )
        .renderlet(function(chart) {
            chart.selectAll('g').on("click", function(p) {
                if (p != null) {
                    var this_state = p.properties.name
                    if (window.list.includes(this_state)) {
                        window.list = window.list.filter(function(el) {
                            return el != this_state;
                        })
                    } else {
                        var list1 = window.list
                        console.log(list)
                        list.push(this_state)

                    }
                    //tweetAnalytics =  get_tweets()
                    world_cloud()
                }

            })
        })
        .title(function(p) {
            return "State: " + names_state[p.key] +
                "\n" +
                "Number of tweets: " + Math.round(p["value"]) + "";
        })


    usChart.on()

    world_cloud();

    dc.renderAll();

};

function world_cloud() {
    //console.log(dataset)
    var fill = d3.scale.category20();
    //what range of font sizes do we want, we will scale the word counts
    var fontSize = d3.scale.log().range([01, 15]);
    //create my cloud object
    var mycloud = d3.layout.cloud().size([300, 300])
        .words([])
        .padding(1)
        .rotate(function() {
            return ~~(Math.random() * 2) * 90;
        })
        // .rotate(function() { return 0; })
        .font("Impact")
        .fontSize(function(d) {
            //console.log(fontSize((d.size)/max*80))
            return fontSize((d.size) / max * 100);
        })
        .on("end", draw)

    function draw(words) {
        d3.select("#wordcloud").selectAll("svg").remove();
        var toto = d3.select("#wordcloud").append("svg")
            .attr("width", 300)
            .attr("height", 300)
            .append("g")
            .attr("transform", "translate(150,150)")
            .selectAll("text")
            .data(words)
            .enter()
            .append("text")
            .style("font-size", function(d) {
                return d.size + "px";
            })
            .style("font-family", "Impact")
            .style("fill", function(d, i) {
                return fill(i);
            })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {

                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) {
                return d.text;
            });


    }
    var max = 0;
    //ajax call

    function get_words(toto) {
        //make ajax call
        if (toto['sentiment'].length == 0) {
            toto['sentiment'] = 'all'
        }
        if (toto['state'].length == 0) {
            toto['state'] = 'all'
        }
        var url = "http://127.0.0.1:5001/word_count?state=" + toto['state'] + "&sentiment=" + toto['sentiment']
        console.log(url)
        d3.json(url, function(json, error) {
            //if (error) return console.log(error);
            json = error;
            var words_array = [];
            for (key in json) {
                words_array.push({
                    text: key,
                    size: json[key]
                })
                if (json[key] > max) {
                    max = json[key];
                }
            }
            mycloud.stop().words(words_array).start();
        })
    };

    if (list.length < 1) {
        window.list = []
        window.list.push('all')
    } else {
        window.list = window.list.filter(function(el) {
            return el != 'all';
        })
    }

    if (list_sentiment.length < 1) {
        window.list_sentiment = []
        window.list_sentiment.push('all')
    } else {
        window.list_sentiment = window.list_sentiment.filter(function(el) {
            return el != 'all';
        })
    }

    get_words({
        state: list,
        sentiment: list_sentiment
    });




}