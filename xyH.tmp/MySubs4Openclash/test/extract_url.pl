#!/usr/bin/perl

use strict; use warnings;
use CGI 'escapeHTML';
use Regexp::Common qw/URI/;
use URI::Find::Schemeless;

my $heuristic = URI::Find::Schemeless->schemeless_uri_re;

my $pattern = qr{
    $RE{URI}{HTTP}{-scheme=>'https?'} |
    $RE{URI}{FTP} |
    $heuristic
}x;

local $/ = '';

while ( my $par = <DATA> ) {
    chomp $par;
    $par =~ s/</&lt;/g;
    $par =~ s/( $pattern ) / linkify($1) /gex;
    print "<p>$par</p>\n";
}

sub linkify {
    my ($str) = @_;
    $str = "http://$str" unless $str =~ /^[fh]t(?:p|tp)/;
    $str = escapeHTML($str);
    sprintf q|<a href="%s">%s</a>|, ($str) x 2;
}