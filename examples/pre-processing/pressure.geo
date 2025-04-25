Mesh.MshFileVersion = 2.2;
cp = newp; Point(cp) = {0,0,0};
p1 = newp; Point(p1) = {1,0,0};
p2 = newp; Point(p2) = {1.2,0,0};
p3 = newp; Point(p3) = {0,1.2,0};
p4 = newp; Point(p4) = {0,1,0};

l1 = newl; Line(l1) = {p1,p2};
l2 = newl; Circle(l2) = {p2,cp,p3};
l3 = newl; Line(l3) = {p3,p4};
l4 = newl; Circle(l4) = {p4,cp,p1};

ll = newll; Line Loop(ll) = {l1,l2,l3,l4};
s01 = news; Surface(s01) = {ll};

Transfinite Line {l1,l2,-l3,-l4} = 20;
Transfinite Surface {s01};
Recombine Surface {s01};
Extrude {0,0,1} {
Surface{s01}; Layers{4}; Recombine;}

Physical Volume("Solid") = {1};
Physical Surface("xsym") = {23};
Physical Surface("ysym") = {15};
Physical Surface("zsym") = {6};
Physical Surface("pressure") = {27};
//Physical Point("d1") = {6};
//Physical Point("d2") = {10};
//Physical Point("i1") = {5};
//Physical Point("i2") = {14};
