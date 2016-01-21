 
  constant C_Y_1       : signed(14 downto 0) := to_signed(4899,  15);
  constant C_Y_2       : signed(14 downto 0) := to_signed(9617,  15);
  constant C_Y_3       : signed(14 downto 0) := to_signed(1868,  15);
  constant C_Cb_1      : signed(14 downto 0) := to_signed(-2764, 15);
  constant C_Cb_2      : signed(14 downto 0) := to_signed(-5428, 15);
  constant C_Cb_3      : signed(14 downto 0) := to_signed(8192,  15);
  constant C_Cr_1      : signed(14 downto 0) := to_signed(8192,  15);
  constant C_Cr_2      : signed(14 downto 0) := to_signed(-6860, 15);
  constant C_Cr_3      : signed(14 downto 0) := to_signed(-1332, 15);
  
  
  
  R_s <= signed('0' & fram1_q(7 downto 0));
  G_s <= signed('0' & fram1_q(15 downto 8));
  B_s <= signed('0' & fram1_q(23 downto 16));
  
  
signal Y_reg_1           : signed(23 downto 0);
  signal Y_reg_2           : signed(23 downto 0);
  signal Y_reg_3           : signed(23 downto 0);
  signal Cb_reg_1          : signed(23 downto 0);
  signal Cb_reg_2          : signed(23 downto 0);
  signal Cb_reg_3          : signed(23 downto 0);
  signal Cr_reg_1          : signed(23 downto 0);
  signal Cr_reg_2          : signed(23 downto 0);
  signal Cr_reg_3          : signed(23 downto 0);
  signal Y_reg             : signed(23 downto 0);
  signal Cb_reg            : signed(23 downto 0);
  signal Cr_reg            : signed(23 downto 0);
  signal R_s               : signed(8 downto 0);
  signal G_s               : signed(8 downto 0);
  signal B_s               : signed(8 downto 0);
 
 
  -------------------------------------------------------------------
  -- RGB to YCbCr conversion
  -------------------------------------------------------------------
  p_rgb2ycbcr : process(CLK, RST)
  begin
    if RST = '1' then
      Y_Reg_1  <= (others => '0');
      Y_Reg_2  <= (others => '0');
      Y_Reg_3  <= (others => '0');
      Cb_Reg_1 <= (others => '0');
      Cb_Reg_2 <= (others => '0');
      Cb_Reg_3 <= (others => '0');
      Cr_Reg_1 <= (others => '0');
      Cr_Reg_2 <= (others => '0');
      Cr_Reg_3 <= (others => '0');
      Y_Reg    <= (others => '0');
      Cb_Reg   <= (others => '0');
      Cr_Reg   <= (others => '0');
    elsif CLK'event and CLK = '1' then
      Y_Reg_1  <= R_s*C_Y_1;
      Y_Reg_2  <= G_s*C_Y_2;
      Y_Reg_3  <= B_s*C_Y_3;
      
      Cb_Reg_1 <= R_s*C_Cb_1;
      Cb_Reg_2 <= G_s*C_Cb_2;
      Cb_Reg_3 <= B_s*C_Cb_3;
      
      Cr_Reg_1 <= R_s*C_Cr_1;
      Cr_Reg_2 <= G_s*C_Cr_
      Cr_Reg_3 <= B_s*C_Cr_3;
      
      Y_Reg  <= Y_Reg_1 + Y_Reg_2 + Y_Reg_3;
      Cb_Reg <= Cb_Reg_1 + Cb_Reg_2 + Cb_Reg_3 + to_signed(128*16384,Cb_Reg'length);
      Cr_Reg <= Cr_Reg_1 + Cr_Reg_2 + Cr_Reg_3 + to_signed(128*16384,Cr_Reg'length);

    end if;
  end process;
  
  Y_8bit  <= unsigned(Y_Reg(21 downto 14));
  Cb_8bit <= unsigned(Cb_Reg(21 downto 14));
  Cr_8bit <= unsigned(Cr_Reg(21 downto 14));
