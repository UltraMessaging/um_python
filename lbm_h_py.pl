#!/usr/bin/env perl
# lbm_h_py.pl
#
# The cffi tools are picky about the format of the include file.
# This tool modifies our "lbm.h" file to cffi's needs:
#   1. Most defintions must be on a single line. Lines that are continued
#      with "\" must be combined to a single long line. A function prototype
#      that spans multiple lines must also be combined to a single long line.
#   2. Get rid of "#include" directives.
#   3. Manifest constants (e.g. "#define FOO 23") must be simplified.
#      No parentheses are allowed, and other constants may not be included
#      symbolically.
#   4. Any "#define"s that can't be simplified are removed.
#   5. A few special-case fixes.

use strict;
use warnings;
use Getopt::Std;
use File::Basename;

my %simple_defines;

# Workaroud for bug http://meltdown.29west.com/bugzilla/show_bug.cgi?id=10557
$simple_defines{"LBTIPC_BEHAVIOR_RCVR_PACED"} = "0";
$simple_defines{"LBTIPC_BEHAVIOR_SRC_PACED"} = "1";

# Main loop; read each line in each file.
while (<>) {
  chomp;  # remove trailing \n

  # glue continuation lines.
  if (s/\\$//) {
    $_ .= <>;
    redo unless eof();
  }

  #glue the function prototypes which are split in multiple lines
  if (/\([^)]+$/) {
    my $cur_line = $_;
	#glue all the lines till you get ")"
    while(<>){
        chomp;
        $cur_line .= $_;
        if(/\)/){
                last;
        }
    }
    print "$cur_line\n";
    next;
  }
   
  #get rid of #include
  if(/#include/){
	  next;
  }


  # Get rid of parenthesis around simple numbers in #defines.
  s/(\#define\s+\w+\s+)\((\d[xA-Fa-fUL\d]*)\)/$1$2/;

  # Get rid of macros: lbm_rcv_retrieve_all_transport_stats, lbm_context_retrieve_rcv_transport_stats, lbm_context_retrieve_src_transport_stats
  next if (/lbm_rcv_retrieve_all_transport_stats\b/);
  next if (/lbm_rcv_retrieve_all_transport_stats_ex.*sizeof/);
  next if (/lbm_context_retrieve_rcv_transport_stats\b/);
  next if (/lbm_context_retrieve_rcv_transport_stats_ex.*sizeof/);
  next if (/lbm_context_retrieve_src_transport_stats\b/);
  next if (/lbm_context_retrieve_src_transport_stats_ex.*sizeof/);

  # Find "simple" definitions (#define sym numeric).  Note that numerics
  # be hex (0x...) and might have U and/or L suffixes (unsigned, long).
  if (/\#define\s+(\w+)\s+(\d[xA-Fa-fUL\d]*)\b/) {
    $simple_defines{$1} = $2;
  }
  elsif (/\#define\s+(\w+)\s+(\w+)\b/) {
    # Found a non-simple definition.  See if the value is an already-seen
    # simple definition.
    my $sym = $1;  my $val=$2;
    if (defined($simple_defines{$val})) {
      # Substitute the previously-seen numeric value for the symbolic value here.
      my $new_val = $simple_defines{$val};
      s/(\#define\s+\w+)\s+\w+\b/$1 $new_val/;
      # Just in case THIS definition is used later, remember its value too.
      $simple_defines{sym} = $new_val;
    }
  else {print STDERR "cant find simple_defines{$val}\n";}
  }

  print "$_\n";
}

# All done.
exit(0);
