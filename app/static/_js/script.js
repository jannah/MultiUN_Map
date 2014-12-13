/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


Histogram = function(target, data, width, height, title) {
    console.log(data);
//    console.log($(this).parent());

//    $(this).parent().append("TESTING")
    data.map(function(d, i, a) {
        a[i]['label'] = d.values + ' ' + d.key;
    });
    console.log(data);
    var w = width, titleH = 30, h = height - titleH;


    var max = d3.max(data, function(d)
    {
        //            console.log(d);
        return d.values;
    });
    var min = d3.min(data, function(d)
    {
        return d.values;
    });
    var yScale = d3.scale.ordinal().rangeBands([0, h], .1, 1)
            .domain(data.map(function(d)
            {
                return d.label;
            }));
//    var yLabels = data.map(function(d) {
////        console.log(d);
//        return d.values + ' ' + d.key;
//    })
//    console.log(yLabels)
    var xScale = d3.scale.linear().domain([0, max]).range([0, w]);
    var yAxis = d3.svg.axis().scale(yScale).orient('left')
//            .tickValues(yLabels);
    var svg = d3.select(target).append('svg')
            .attr({
                height: height, width: width, class: 'histogram'}
            );
    var title = svg.append('g').append('text')
            .attr({
                x: w / 2, y: titleH
            })
            .style({'text-anchor': 'middle'})
            .text(title);
    var bars = svg.append('g')
            .attr("transform", "translate(" + 0 + "," + titleH + ")")
            .selectAll('rect')
            .data(data).enter()
            .append('rect')
            .attr({
                x: 0,
                y: function(d) {
                    return yScale(d.label);
                },
                height: yScale.rangeBand(),
                width: function(d) {
                    return xScale(d.values);
                }
            })
            .on('click',function(d) {
                alert(d.label);
            })
    var yAxisGroup = svg.append('g').attr(
            {
                class: "y axis",
                width: w,
                height: h
            }).append("g")
            .attr("transform", "translate(" + 0 + "," + titleH + ")")
            .call(yAxis)
            .selectAll("text")
            .style("text-anchor", "start")
            .attr({"dx":"2em", "dy": ".2em",'unselectable':'on'})
            .classed('unselectable', true)
               .on('click',function(d) {
                alert(d);
            })
//            .attr("transform", function(d) {
//                return "rotate(45)";
//            });

}
