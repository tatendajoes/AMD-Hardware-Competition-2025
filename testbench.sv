// tb_peak_abs.sv
`timescale 1ns/1ps

module tb_peak_abs;

  localparam int WIDTH     = 16;
  localparam int N_SAMPLES = 16;

  logic clk, rst_n;
  logic start, in_valid;
  logic signed [WIDTH-1:0] sample_in;

  logic out_valid;
  logic [WIDTH-1:0] peak_out;
  logic [$clog2(N_SAMPLES)-1:0] peak_idx;

  // DUT
  peak_abs #(.WIDTH(WIDTH), .N_SAMPLES(N_SAMPLES)) dut (
    .clk(clk), .rst_n(rst_n),
    .start(start), .in_valid(in_valid),
    .sample_in(sample_in),
    .out_valid(out_valid),
    .peak_out(peak_out),
    .peak_idx(peak_idx)
  );

  // Clock
  initial clk = 0;
  always #5 clk = ~clk; // 100 MHz

  // VCD dump (works in xrun; add -access +rwc when running)
  initial begin
    $dumpfile("tb_peak_abs.vcd");
    $dumpvars(0, tb_peak_abs);
  end

  // Stimulus
  logic signed [WIDTH-1:0] test_vec [0:N_SAMPLES-1];
  int i;
  int expected_peak;
  int expected_idx;
  int abs_val;     // <- declare first, assign later
  int timeout;     // <- declare first, assign later

  initial begin
    // Reset
    rst_n = 0; start = 0; in_valid = 0; sample_in = '0;
    expected_peak = 0; expected_idx = 0;
    repeat (4) @(posedge clk);
    rst_n = 1;
    @(posedge clk);

    // Samples
    test_vec[0]  =  16'sd12;
    test_vec[1]  = -16'sd45;
    test_vec[2]  =  16'sd78;
    test_vec[3]  = -16'sd300;
    test_vec[4]  =  16'sd150;
    test_vec[5]  = -16'sd200;
    test_vec[6]  =  16'sd50;
    test_vec[7]  =  16'sd0;
    test_vec[8]  = -16'sd1024;
    test_vec[9]  =  16'sd77;
    test_vec[10] =  16'sd25;
    test_vec[11] = -16'sd999;
    test_vec[12] =  16'sd500;
    test_vec[13] = -16'sd250;
    test_vec[14] =  16'sd1023;
    test_vec[15] = -16'sd700;

    // Software expected
    expected_peak = 0;
    expected_idx  = 0;
    for (i = 0; i < N_SAMPLES; i++) begin
      abs_val = (test_vec[i] < 0) ? -test_vec[i] : test_vec[i];
      if (abs_val > expected_peak) begin
        expected_peak = abs_val;
        expected_idx  = i;
      end
    end

    // Start frame
    @(posedge clk); start <= 1;
    @(posedge clk); start <= 0;

    // Feed N samples
    for (i = 0; i < N_SAMPLES; i++) begin
      @(posedge clk);
      in_valid  <= 1;
      sample_in <= test_vec[i];
    end
    @(posedge clk);
    in_valid <= 0;

    // Wait for result with timeout
    timeout = 0;
    while (!out_valid && timeout < 1000) begin
      @(posedge clk);
      timeout++;
    end
    if (!out_valid) begin
      $display("TIMEOUT waiting for out_valid");
      $finish;
    end

    // Sample outputs (align to pulse edge)
    @(posedge clk);
    $display("DUT peak_out=%0d (exp %0d), peak_idx=%0d (exp %0d)",
              peak_out, expected_peak, peak_idx, expected_idx);

    if ((peak_out == expected_peak) && (peak_idx == expected_idx))
      $display("TEST PASSED");
    else
      $display("TEST FAILED");

    #20 $finish;
  end

endmodule
