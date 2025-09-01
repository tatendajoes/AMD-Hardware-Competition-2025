module peak_abs #(
  parameter int WIDTH      = 16,
  parameter int N_SAMPLES  = 1024
) (
  input  logic                     clk,
  input  logic                     rst_n,

  input  logic                     start,      // 1-cycle pulse
  input  logic                     in_valid,   // sample_in valid
  input  logic signed [WIDTH-1:0]  sample_in,

  output logic                     out_valid,  // 1-cycle pulse at end-of-frame
  output logic [WIDTH-1:0]         peak_out,   // |x|max (unsigned)
  output logic [$clog2(N_SAMPLES)-1:0] peak_idx
);

  // State
  logic running;
  logic [$clog2(N_SAMPLES):0]      count;        // #samples seen in this frame
  logic [WIDTH-1:0]                peak_reg;
  logic [$clog2(N_SAMPLES)-1:0]    peak_idx_reg;

  // Registered pulse when we accept the last sample
  logic out_valid_r;

  // abs with saturation for most-negative value
  function automatic [WIDTH-1:0] abs_sat(input logic signed [WIDTH-1:0] x);
    logic [WIDTH-1:0] min_mag;
    begin
      min_mag = 1'b1 << (WIDTH-1);     // 1000...0
      if (x[WIDTH-1]) begin
        abs_sat = (x == $signed(min_mag)) ? min_mag : $unsigned(-x);
      end else begin
        abs_sat = $unsigned(x);
      end
    end
  endfunction

  // Outputs
  assign out_valid = out_valid_r;
  assign peak_out  = peak_reg;
  assign peak_idx  = peak_idx_reg;

  // Main
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      running      <= 1'b0;
      count        <= '0;
      peak_reg     <= '0;
      peak_idx_reg <= '0;
      out_valid_r  <= 1'b0;
    end else begin
      // default: drop the 1-cycle pulse
      out_valid_r <= 1'b0;

      // Start a new frame
      if (start) begin
        running      <= 1'b1;
        count        <= '0;
        peak_reg     <= '0;
        peak_idx_reg <= '0;
      end

      if (running && in_valid) begin
        // Update peak
        logic [WIDTH-1:0] abs_val;
        abs_val = abs_sat(sample_in);
        if (abs_val >= peak_reg) begin
          peak_reg     <= abs_val;
          peak_idx_reg <= count[$clog2(N_SAMPLES)-1:0];
        end

        // If this is the last sample, emit pulse now
        if (count == N_SAMPLES-1) begin
          out_valid_r <= 1'b1;
          running     <= 1'b0;
          count       <= '0;         // prepare for next frame
        end else begin
          count <= count + 1'b1;
        end
      end
    end
  end

endmodule
